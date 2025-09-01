from __future__ import annotations

import json
import logging
from typing import Optional, Sequence, Tuple, List, Dict, Any
import os
from anyio import to_thread
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_db_session, settings
from app.services.credits_service import CreditsService
from app.models import StripeCustomer

# Import Stripe at module level to avoid late import errors
try:
    import stripe
except ImportError:
    stripe = None

logger = logging.getLogger(__name__)
webhooks_router = APIRouter()


def _parse_int(val: Optional[str]) -> Optional[int]:
    try:
        return int(val) if val is not None else None
    except Exception:
        return None


async def _resolve_user_id(db: AsyncSession, stripe_customer_id: Optional[str], meta: dict) -> Optional[str]:
    """IMPROVED: Robust User-ID Resolution from Stripe Checkout Session"""
    # 1) Mapping table lookup
    if stripe_customer_id:
        row = await db.execute(
            StripeCustomer.__table__.select().where(StripeCustomer.stripe_customer_id == stripe_customer_id)  # type: ignore[attr-defined]
        )
        existing = row.first()
        if existing and existing[0].user_id:  # type: ignore[index]
            logger.info(f"✅ User-ID from StripeCustomer: {existing[0].user_id}")  # type: ignore[index]
            return existing[0].user_id  # type: ignore[index]
    
    # 2) Metadata fallback (primary method for new customers)
    if isinstance(meta, dict):
        user_id = meta.get("user_id")
        if user_id:
            logger.info(f"✅ User-ID from metadata: {user_id}")
            return user_id
        else:
            logger.error(f"❌ No user_id in metadata. Available keys: {list(meta.keys())}")
            logger.error(f"❌ Full metadata: {meta}")
    else:
        logger.error(f"❌ Metadata is not a dict: {type(meta)} = {meta}")
    
    logger.error("❌ CRITICAL: All user resolution methods failed!")
    return None


async def _resolve_user_id_FIXED(db: AsyncSession, stripe_customer_id: Optional[str], meta: dict) -> Optional[str]:
    """NEUER ANSATZ: Robuste User-ID Resolution - The Ultimate Fix"""
    # 1. DIREKTE Metadata-Prüfung ZUERST (nicht erst StripeCustomer lookup!)
    if isinstance(meta, dict) and meta.get("user_id"):
        user_id = str(meta["user_id"]).strip()
        if user_id:
            logger.info(f"✅ User-ID from metadata: {user_id}")
            return user_id
    
    # 2. StripeCustomer lookup als Fallback
    if stripe_customer_id:
        # KORRIGIERTE SQLAlchemy Query
        result = await db.execute(
            select(StripeCustomer.user_id).where(StripeCustomer.stripe_customer_id == stripe_customer_id)
        )
        row = result.first()
        if row and row[0]:
            logger.info(f"✅ User-ID from StripeCustomer lookup: {row[0]}")
            return str(row[0])
    
    # 3. DEBUGGING: Log alle verfügbaren Daten
    logger.error(f"❌ USER RESOLUTION FAILED:")
    logger.error(f"   stripe_customer_id: {stripe_customer_id}")
    logger.error(f"   metadata type: {type(meta)}")
    logger.error(f"   metadata content: {meta}")
    if isinstance(meta, dict):
        logger.error(f"   metadata keys: {list(meta.keys())}")
        for key, value in meta.items():
            logger.error(f"   metadata[{key}] = {value} (type: {type(value)})")
    
    return None


def _build_price_map() -> Dict[str, int]:
    """
    Build a mapping of Stripe price_id -> credit amount from settings.
    Sources (priority order):
      1) STRIPE_PRICE_TO_CREDITS_JSON (JSON object)
      2) Individual envs STRIPE_PRICE_{SMALL,MEDIUM,LARGE}_ID with default credits
    """
    mp: Dict[str, int] = {}
    # JSON mapping first
    raw = (settings.STRIPE_PRICE_TO_CREDITS_JSON or "").strip()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                for k, v in data.items():
                    try:
                        if isinstance(k, str):
                            mp[k] = int(v)
                    except Exception:
                        continue
        except Exception:
            logger.warning("Invalid STRIPE_PRICE_TO_CREDITS_JSON; ignoring")
    # Fallback trio
    trio: List[Tuple[Optional[str], int]] = [
        (getattr(settings, "STRIPE_PRICE_SMALL_ID", None), getattr(settings, "STRIPE_PRICE_SMALL_CREDITS", 100)),
        (getattr(settings, "STRIPE_PRICE_MEDIUM_ID", None), getattr(settings, "STRIPE_PRICE_MEDIUM_CREDITS", 500)),
        (getattr(settings, "STRIPE_PRICE_LARGE_ID", None), getattr(settings, "STRIPE_PRICE_LARGE_CREDITS", 1500)),
    ]
    for pid, credits in trio:
        if pid:
            try:
                mp[str(pid)] = int(credits)
            except Exception:
                pass
    return mp


def _sum_credits_for_prices(price_items: Sequence[Tuple[str, int]]) -> Tuple[int, str]:
    """
    Given a sequence of (price_id, quantity), return (total_credits, reason).
    Reason includes single price id if only one distinct price is present.
    """
    price_map = _build_price_map()
    total = 0
    distinct: List[str] = []
    for pid, qty in price_items:
        if pid not in price_map:
            continue
        if pid not in distinct:
            distinct.append(pid)
        total += price_map[pid] * max(1, int(qty))
    if len(distinct) == 1:
        reason = f"purchase:{distinct[0]}"
    else:
        reason = "purchase:multiple"
    return total, reason


async def _collect_prices_from_checkout_session(session_obj: Dict[str, Any]) -> List[Tuple[str, int]]:
    """Return list of (price_id, quantity) from checkout.session.completed."""
    sid = session_obj.get("id")
    if not sid:
        return []
    try:
        # Stripe Python SDK is synchronous; run in thread to avoid blocking the event loop
        items = await to_thread.run_sync(lambda: stripe.checkout.Session.list_line_items(sid, limit=20))  # type: ignore[attr-defined]
    except Exception as e:
        logger.warning("Failed to fetch line items for session %s: %s", sid, e)
        return []
    out: List[Tuple[str, int]] = []
    for li in items.get("data", []) or []:
        price = (li.get("price") or {})
        pid = price.get("id")
        qty = li.get("quantity") or 1
        if isinstance(pid, str):
            out.append((pid, int(qty)))
    return out


def _collect_prices_from_invoice_obj(inv_obj: Dict[str, Any]) -> List[Tuple[str, int]]:
    out: List[Tuple[str, int]] = []
    lines = (inv_obj.get("lines") or {}).get("data") or []
    for li in lines:
        price = (li.get("price") or {})
        pid = price.get("id")
        qty = li.get("quantity") or 1
        if isinstance(pid, str):
            out.append((pid, int(qty)))
    return out


@webhooks_router.post("/webhooks/stripe", summary="Stripe webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        # Misconfigured – do not process
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    if not sig_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature")

    # Try verifying with Stripe SDK if available, else in E2E mode trust the payload
    try:
        if stripe is None:
            raise ImportError("Stripe module not available")
        # Set API key only if available; when absent, we fall back to metadata for credits
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY  # type: ignore[arg-type]
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,  # type: ignore[arg-type]
        )
    except Exception as e:
        # If stripe SDK missing or verification failed, allow E2E mode to proceed with raw JSON
        e2e_mode = (os.getenv('E2E_TEST_MODE') or '').strip() not in ('', '0', 'false', 'False')
        if not e2e_mode:
            logger.exception("Stripe webhook parse error")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload") from e
        try:
            event = json.loads(payload.decode('utf-8'))
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload (e2e)")

    # Handle crediting events by summing credits from price IDs
    etype = str(event.get("type"))
    if etype in {"checkout.session.completed", "invoice.paid"}:
        obj = event["data"]["object"]
        stripe_customer_id = obj.get("customer") or obj.get("customer_id")
        price_items: List[Tuple[str, int]] = []
        if etype == "checkout.session.completed":
            price_items = await _collect_prices_from_checkout_session(obj)
        elif etype == "invoice.paid":
            # Prefer embedded lines; if not present, ACK gracefully without credits
            price_items = _collect_prices_from_invoice_obj(obj)

        credits, reason = _sum_credits_for_prices(price_items)
        if credits <= 0:
            # Fallback: trust metadata.credits set at Checkout creation on our server
            meta = obj.get("metadata") or {}
            mcredits = _parse_int(meta.get("credits") if isinstance(meta, dict) else None)
            if mcredits and mcredits > 0:
                credits = int(mcredits)
                # Prefer a price-aware reason if metadata contains price_id; otherwise mark as meta
                mprice = (meta.get("price_id") if isinstance(meta, dict) else None) or None
                reason = f"purchase:{mprice}" if isinstance(mprice, str) and mprice else "purchase:meta"
            else:
                # No known price mapping and no metadata fallback; acknowledge without action
                logger.info(
                    "stripe_webhook: no mapped credits for event %s (prices=%s, meta_credits=%s)",
                    event.get("id"), price_items, mcredits,
                )
                return JSONResponse(status_code=200, content={"ok": True, "skipped": "no_mapped_prices"})

        svc = CreditsService(db)
        # Resolve user id via mapping table or metadata fallback (from checkout metadata)
        # Use the FIXED resolution function for better reliability
        user_id = await _resolve_user_id_FIXED(db, stripe_customer_id, obj.get("metadata") or {})
        if not user_id:
            logger.warning("stripe_webhook: missing user_id for customer %s", stripe_customer_id)
            return JSONResponse(status_code=200, content={"ok": True, "skipped": "no_user_mapping"})

        # Ensure mapping is recorded
        await svc.ensure_customer(user_id=user_id, stripe_customer_id=stripe_customer_id)
        try:
            await svc.credit_purchase(
                user_id=user_id,
                delta=int(credits),
                reason=reason,
                stripe_event_id=str(event.get("id")),
            )
            await db.commit()
        except Exception as e:
            # Likely idempotent duplicate; log and ack
            await db.rollback()
            logger.info("stripe_webhook: duplicate or error crediting: %s", str(e))
        return JSONResponse(status_code=200, content={"ok": True})

    # For benign events that can occur during tests, ACK explicitly
    if etype in {"checkout.session.expired", "payment_intent.canceled"}:
        logger.info("stripe_webhook: benign event %s", etype)
        return JSONResponse(status_code=200, content={"ok": True, "skipped": etype})

    # For all other events, just ACK (can expand later)
    return JSONResponse(status_code=200, content={"ok": True})


# Backward/alternate path commonly used by clients: /api/stripe/webhook
# Keep out of OpenAPI to avoid confusion with public API; handled identically.
@webhooks_router.post("/api/stripe/webhook", include_in_schema=False)
async def stripe_webhook_alias(request: Request, db: AsyncSession = Depends(get_db_session)):
    return await stripe_webhook(request, db)


# OLD EMERGENCY ROUTE REMOVED - Now handled by Ultimate Webhook Handler in base.py
# This eliminates route conflicts and ensures the Ultimate handler is used
