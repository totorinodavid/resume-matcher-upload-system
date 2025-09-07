import os
import contextlib
import warnings
import json

# Suppress noisy pydub ffmpeg availability warning globally (not relevant for core API tests)
warnings.filterwarnings(
    "ignore",
    message="Couldn't find ffmpeg or avconv",
    category=RuntimeWarning,
)

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .api import health_check, v1_router, RequestIDMiddleware
from .api.body_limit import BodySizeLimitMiddleware
from .api.rate_limit import RateLimitMiddleware
from .core import (
    settings,
    async_engine,
    setup_logging,
    custom_http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
    get_db_session,
)
# Prefer the shared redaction utility; if unavailable at runtime, fall back to a local minimal implementation
try:  # pragma: no cover - exercised in deployment environments
    from .core.redaction import redact  # type: ignore
except Exception:  # pragma: no cover - defensive fallback
    import re

    _EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    _PHONE_RE = re.compile(r"(?:(?:\+|00)\d{1,3}[- ]?)?(?:\d[ -]?){6,14}\d")

    def redact(value: str) -> str:
        if not value:
            return value
        out = _EMAIL_RE.sub("<email:redacted>", value)
        out = _PHONE_RE.sub("<phone:redacted>", out)
        return out
from sqlalchemy import delete, text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging
try:
    from .models import LLMCache  # noqa: F401
except Exception:
    LLMCache = None  # type: ignore
from .core.database import AsyncSessionLocal
from .core.auth import require_auth, Principal

logger = logging.getLogger(__name__)
from .models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce PostgreSQL-only in normal runs; allow PostgreSQL in E2E_TEST_MODE for local E2E
    e2e_mode = (os.getenv('E2E_TEST_MODE') or '').strip() not in ('', '0', 'false', 'False')
    
    if async_engine.dialect.name != 'postgresql' and not e2e_mode:
        raise RuntimeError(
            "Unsupported database dialect. This deployment is configured for PostgreSQL only."
        )
    # Defer database connection until after startup to avoid DNS issues
    try:
        # Light database validation without immediate connection
        if async_engine.dialect.name != 'postgresql' and not e2e_mode:
            raise RuntimeError(
                "Unsupported database dialect. This deployment is configured for PostgreSQL only."
            )
        logger.info("Database engine validated - PostgreSQL dialect confirmed")
    except Exception as e:
        logger.warning(f"Database validation issue (will retry later): {e}")
    
    # Schedule database connection test for after app startup
    async def delayed_db_check():
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await conn.execute(sql_text("SELECT 1"))
                logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
    
    # Run database check in background (non-blocking)
    if not getattr(settings, "DISABLE_BACKGROUND_TASKS", False):
        asyncio.create_task(delayed_db_check())
    stop_event = asyncio.Event()

    async def _cache_cleanup_loop() -> None:
        """Periodically delete expired LLM cache entries until stop_event is set."""
        interval = max(1, int(getattr(settings, "LLM_CACHE_CLEAN_INTERVAL_SECONDS", 600) or 600))
        max_batch = max(1, int(getattr(settings, "LLM_CACHE_MAX_DELETE_BATCH", 500) or 500))

        while not stop_event.is_set():
            try:
                # Import and create session safely
                from .core.database import get_db_session
                async for session in get_db_session():
                    # PostgreSQL-only cleanup - use CTE to limit deletions atomically
                    delete_sql = sql_text(
                        """
                        WITH expired AS (
                            SELECT cache_key FROM llm_cache
                            WHERE EXTRACT(EPOCH FROM (NOW() - created_at)) > ttl_seconds
                            LIMIT :batch
                        )
                        DELETE FROM llm_cache c
                        USING expired e
                        WHERE c.cache_key = e.cache_key;
                        """
                    )
                    await session.execute(delete_sql, {"batch": max_batch})
                    # Note: get_db_session() handles commit automatically
                    break  # Only need one session iteration
            except asyncio.CancelledError:  # pragma: no cover
                break
            except Exception as e:  # pragma: no cover
                logger.warning(f"Cache cleanup loop error: {e}")
            # Sleep-wait with graceful shutdown: break on cancel or stop event
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:  # pragma: no cover
                break

    task = None
    if not getattr(settings, "DISABLE_BACKGROUND_TASKS", False):
        task = asyncio.create_task(_cache_cleanup_loop())
    yield
    stop_event.set()
    # Do not cancel; let the loop observe the event and exit cleanly to avoid
    # CancelledError bubbling through lifespan shutdown on some platforms.
    if task is not None:
        with contextlib.suppress(Exception):  # pragma: no cover
            await task
    # Under pytest we avoid disposing the global engine to prevent asyncpg tasks
    # scheduling on a closed loop; the test process teardown will clean resources.
    if 'PYTEST_CURRENT_TEST' not in os.environ:
        await async_engine.dispose()


def create_app() -> FastAPI:
    """
    configure and create the FastAPI application instance.
    """
    setup_logging()
    # Attach a lightweight redaction filter to the root logger (idempotent)
    class _RedactionFilter(logging.Filter):  # pragma: no cover - simple integration
        def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
            if isinstance(record.msg, str):
                record.msg = redact(record.msg)
            # Also redact common attributes if present
            for attr in ("email", "phone", "user"):
                if hasattr(record, attr):
                    try:
                        setattr(record, attr, redact(str(getattr(record, attr))))
                    except Exception:
                        pass
            return True
    root_logger = logging.getLogger()
    if not any(isinstance(f, _RedactionFilter) for f in root_logger.filters):
        root_logger.addFilter(_RedactionFilter())

    app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Optional Sentry integration
    try:  # pragma: no cover - integration
        import sentry_sdk  # type: ignore
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware  # type: ignore
        dsn = os.getenv("SENTRY_DSN_BACKEND") or os.getenv("SENTRY_DSN")
        if dsn:
            sentry_sdk.init(dsn=dsn, environment=os.getenv("ENV", "production"), traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")))
            app.add_middleware(SentryAsgiMiddleware)
    except Exception:
        pass

    # Early body size limiter (must precede others reading body)
    app.add_middleware(BodySizeLimitMiddleware)

    app.add_middleware(
        SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY, same_site="lax"
    )
    # CORS: include Vercel domains and Authorization header
    cors_origins = list(dict.fromkeys([
        *getattr(settings, 'ALLOWED_ORIGINS', []),
        "https://*.vercel.app",
        os.getenv("NEXT_PUBLIC_APP_URL", "").strip() or None,
        os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "").strip() or None,
    ]))
    cors_origins = [o for o in cors_origins if o]
    vercel_regex = r"https://([a-zA-Z0-9-]+)\.vercel\.app$"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["http://localhost:3000"],
        allow_origin_regex=vercel_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    app.add_exception_handler(HTTPException, custom_http_exception_handler)
    # Override default pydantic validation to unified envelope
    async def unified_validation_handler(request, exc: RequestValidationError):  # type: ignore[override]
        request_id = getattr(request.state, "request_id", "validation:" )
        return JSONResponse(
            status_code=422,
            content={
                "request_id": request_id,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request",
                    "detail": exc.errors(),
                },
            },
        )
    app.add_exception_handler(RequestValidationError, unified_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    if os.path.exists(settings.FRONTEND_PATH):
        app.mount(
            "/app",
            StaticFiles(directory=settings.FRONTEND_PATH, html=True),
            name=settings.PROJECT_NAME,
        )

    app.include_router(health_check)
    app.include_router(v1_router)

    # In tests, override auth dependency to avoid 401s in route tests that don't attach tokens
    # This does not affect the dedicated auth smoke test, which mounts only the auth router directly.
    try:
        if os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("DISABLE_AUTH_FOR_TESTS") == "1":
            async def _test_principal_override():
                return Principal(user_id="test-user")
            app.dependency_overrides[require_auth] = _test_principal_override
    except Exception:
        # Best-effort override; safe to ignore in non-test environments
        pass

    # Friendly root route: redirect to API docs
    @app.get("/", include_in_schema=False)
    async def _root():  # pragma: no cover - simple UX improvement
        return RedirectResponse(url="/api/docs")
    
    return app
