import os
import sys
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Literal, cast, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# Helper: derive sync/async DB URLs from unified DATABASE_URL
# PostgreSQL-only configuration for Render PostgreSQL consistency
# ──────────────────────────────────────────────────────────────────────────────
def _derive_db_urls(db_url: str) -> Tuple[str, str]:
    """Convert any PostgreSQL URL format to proper sync/async URLs for Render PostgreSQL."""
    url = db_url.strip()
    if not url:
        raise ValueError("DATABASE_URL is required. Use PostgreSQL format: postgres://user:pass@localhost:5432/dbname")
    
    # Normalize postgres:// to postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Ensure PostgreSQL URL
    if not url.startswith("postgresql://") and not url.startswith("postgresql+"):
        raise ValueError(f"Only PostgreSQL is supported. Got: {url[:20]}... Use format: postgres://user:pass@localhost:5432/dbname")
    
    # Sync URL: Use psycopg driver
    if url.startswith("postgresql+psycopg://"):
        sync_url = url
    elif url.startswith("postgresql://"):
        sync_url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        sync_url = url
    
    # Async URL: Use asyncpg driver
    if url.startswith("postgresql+asyncpg://"):
        async_url = url
    elif url.startswith("postgresql+psycopg://"):
        async_url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_url = url
    
    # Convert sslmode to ssl for asyncpg and add SSL enforcement
    if "sslmode=require" in async_url and "ssl=" not in async_url:
        async_url = async_url.replace("?sslmode=require", "?ssl=require").replace("&sslmode=require", "&ssl=require")
    elif "ssl=" not in async_url and "sslmode=" not in async_url:
        # Add SSL requirement for Render PostgreSQL if not specified
        separator = "?" if "?" not in async_url else "&"
        async_url = f"{async_url}{separator}ssl=require"
    
    return (sync_url, async_url)


# SAFE: Database URL resolution that doesn't fail at import time
def _get_database_url_safe() -> str:
    """Get DATABASE_URL with safe fallback that won't crash at import time"""
    
    # 1. Try DATABASE_URL (should be auto-injected by Render PostgreSQL)
    db_url = os.getenv("DATABASE_URL", "").strip()
    if db_url:
        return db_url
    
    # 2. Try ASYNC_DATABASE_URL (explicit setting)
    async_url = os.getenv("ASYNC_DATABASE_URL", "").strip()
    if async_url:
        return async_url
        
    # 3. Try FALLBACK_DATABASE_URL (manual override)
    fallback_url = os.getenv("FALLBACK_DATABASE_URL", "").strip()
    if fallback_url:
        return fallback_url
    
    # 4. Try MANUAL_DATABASE_URL (emergency override)
    manual_url = os.getenv("MANUAL_DATABASE_URL", "").strip()
    if manual_url:
        return manual_url
    
    # 5. Development fallback (localhost) - THIS WON'T WORK IN PRODUCTION
    default_url = "postgresql://postgres:password@localhost:5432/resume_matcher"
    return default_url

# Get primary database URL with SAFE logic (no crashes at import time)
try:
    _UNIFIED_DB = _get_database_url_safe()
    _SYNC_DEFAULT, _ASYNC_DEFAULT = _derive_db_urls(_UNIFIED_DB)
except Exception:
    # EMERGENCY FALLBACK: If even this fails, use localhost URLs
    _SYNC_DEFAULT = "postgresql+psycopg://postgres:password@localhost:5432/resume_matcher"
    _ASYNC_DEFAULT = "postgresql+asyncpg://postgres:password@localhost:5432/resume_matcher"


class Settings(BaseSettings):
    # Project Configuration
    PROJECT_NAME: str = "Resume Matcher"
    FRONTEND_PATH: str = os.path.join(os.path.dirname(__file__), "frontend", "assets")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://gojob.ing",
        "https://www.gojob.ing"
    ]
    
    # Database Configuration (PostgreSQL-only)
    DATABASE_URL: Optional[str] = None  # Unified database URL
    SYNC_DATABASE_URL: str = _SYNC_DEFAULT
    ASYNC_DATABASE_URL: str = _ASYNC_DEFAULT
    DB_ECHO: bool = False
    DB_POOL_SIZE: Optional[int] = None
    DB_MAX_OVERFLOW: Optional[int] = None
    DB_POOL_TIMEOUT: Optional[int] = None
    
    # Security Configuration
    SECRET_KEY: Optional[str] = None
    SESSION_SECRET_KEY: Optional[str] = None
    
    # Environment Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PYTHONDONTWRITEBYTECODE: int = 1
    
    # CORS Configuration
    CORS_ORIGINS: Optional[str] = None  # JSON string for complex CORS setup
    
    # LLM Configuration
    LLM_PROVIDER: Optional[str] = "openai"
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: Optional[str] = "gpt-4o-mini"  # Fixed field name
    LLM_FALLBACK_MODEL: Optional[str] = "gpt-4o-mini"  # Fixed field name
    OPENAI_API_KEY: Optional[str] = None  # Compatibility alias
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: Optional[str] = "openai"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_BASE_URL: Optional[str] = None
    EMBEDDING_MODEL: Optional[str] = "text-embedding-3-small"
    # Pricing (USD per 1K tokens)
    LLM_PRICE_IN_PER_1K: float = 0.00015
    LLM_PRICE_OUT_PER_1K: float = 0.00060
    EMBEDDING_PRICE_PER_1K: float = 0.00013
    # LLM generation tuning
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_OUTPUT_TOKENS: int = 800
    # Matching feature flags and tuning
    MATCH_ENABLE_COVERAGE_MATRIX: bool = True
    MATCH_ENABLE_CHUNK_RETRIEVAL: bool = True
    MATCH_CHUNK_SIZE_TOKENS: int = 600
    MATCH_CHUNK_OVERLAP_TOKENS: int = 64
    MATCH_TOP_K_CHUNK_PAIRS: int = 3
    # Improvement tuning
    IMPROVE_EQUIVALENCE_THRESHOLD: float = 0.82  # cosine threshold for dynamic equivalence in baseline weave
    IMPROVE_ALWAYS_CORE_TECH: bool = False       # if true, always include a Core Technologies line even when no missing keywords
    IMPROVE_LLM_ATTEMPTS: int = 1                # single attempt for lower latency
    # Target uplift enforcement (optional)
    IMPROVE_ENFORCE_MIN_UPLIFT: bool = False     # if true, attempt to reach at least IMPROVE_TARGET_UPLIFT_PERCENT relative uplift
    IMPROVE_TARGET_UPLIFT_PERCENT: float = 0.20  # 20% relative uplift target (0.20 == +20%)
    IMPROVE_MAX_ROUNDS: int = 0                  # no extra rounds by default to protect latency
    IMPROVE_TEMPERATURE_SWEEP: List[float] = [0.4]  # single temp pass for speed
    IMPROVE_MAX_OUTPUT_TOKENS_BOOST: int = 1000  # keep output length bounded for latency
    # Early-stop when recent rounds yield negligible uplift relative to base
    IMPROVE_EARLY_STOP_DELTA: float = 0.01       # be less aggressive; stop if <1% relative uplift gain over recent rounds
    IMPROVE_EARLY_STOP_PATIENCE_ROUNDS: int = 3  # wait longer before stopping to allow exploration
    # Strict mode: require LLM + Embeddings; if unavailable, fail (no fallback)
    REQUIRE_LLM_STRICT: bool = True
    # Resume section labels (to avoid hardcoded language in weaving)
    RESUME_HEADERS_SKILLS: List[str] = ["Fähigkeiten", "Skills", "Kompetenzen"]
    RESUME_HEADERS_PROFILE: List[str] = ["Profil", "Profile", "Kurzprofil", "Summary"]
    RESUME_HEADERS_EXPERIENCE: List[str] = ["Berufserfahrung", "Experience", "Erfahrung", "Professional Experience"]
    RESUME_CORE_TECH_LABEL: str = "Kompetenzen"
    RESUME_EXPERIENCE_WEAVE_PREFIX: str = "Arbeit mit"
    RESUME_SUGGESTED_ADDITIONS_HEADER: str = "Vorgeschlagene Ergänzungen (Baseline)"
    RESUME_MISSING_KEYWORDS_LABEL: str = "Fehlende Schlüsselbegriffe"
    # Rate limiting & security
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 60  # requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    MAX_UPLOAD_SIZE_MB: int = 5  # Max resume upload size
    MAX_JSON_BODY_SIZE_KB: int = 256  # For JSON endpoints (job upload etc.)
    # Cache maintenance
    LLM_CACHE_CLEAN_INTERVAL_SECONDS: int = 600  # 10 min default
    LLM_CACHE_MAX_DELETE_BATCH: int = 500
    # Testing / deterministic execution
    DISABLE_BACKGROUND_TASKS: bool = False  # If True, run normally deferred tasks inline (helps tests / prevents loop-close races)
    # Auth (NextAuth.js)
    NEXTAUTH_SECRET: Optional[str] = None
    NEXTAUTH_URL: Optional[str] = None
    # Stripe configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    # Frontend URL for redirects (billing, success pages)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Storage Configuration
    USE_CLOUD_STORAGE: bool = False  # Development: False, Production: True
    LOCAL_STORAGE_PATH: str = "./uploads"  # Local storage für Development
    CLOUD_STORAGE_BASE_URL: Optional[str] = None  # z.B. "https://bucket.s3.amazonaws.com"
    
    # Stripe price mapping -> credits (Phase 5)
    STRIPE_PRICE_TO_CREDITS_JSON: Optional[str] = None  # JSON object: {"price_xxx": 100, ...}
    STRIPE_PRICE_SMALL_ID: Optional[str] = None
    STRIPE_PRICE_MEDIUM_ID: Optional[str] = None
    STRIPE_PRICE_LARGE_ID: Optional[str] = None
    STRIPE_PRICE_SMALL_CREDITS: int = 100
    STRIPE_PRICE_MEDIUM_CREDITS: int = 500
    STRIPE_PRICE_LARGE_CREDITS: int = 1500
    
    # Credits system controls
    CREDITS_WRITE_FREEZE: bool = False  # Emergency freeze for credit operations

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()


_LEVEL_BY_ENV: dict[Literal["production", "staging", "local"], int] = {
    "production": logging.INFO,
    "staging": logging.DEBUG,
    "local": logging.DEBUG,
}


def setup_logging() -> None:
    """
    Configure the root logger exactly once,

    * Console only (StreamHandler -> stderr)
    * ISO - 8601 timestamps
    * Env - based log level: production -> INFO, else DEBUG
    * Prevents duplicate handler creation if called twice
    """
    root = logging.getLogger()
    if root.handlers:
        return

    raw_env = getattr(settings, "ENV", "production")
    env_norm = str(raw_env).lower()
    # Fallback to production if unexpected value
    if env_norm == "staging":
        env_key: Literal["staging"] = "staging"
    elif env_norm == "local":
        env_key = "local"  # type: ignore[assignment]
    else:
        env_key = "production"  # type: ignore[assignment]
    level = _LEVEL_BY_ENV[cast(Literal["production", "staging", "local"], env_key)]

    formatter = logging.Formatter(
        fmt="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)

    for noisy in ("sqlalchemy.engine", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
