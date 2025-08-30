import json
import pytest
import httpx

from app.base import create_app
from app.services.credits_service import CreditsService


pytestmark = pytest.mark.asyncio


async def test_service_credit_idempotency(db_session):
    svc = CreditsService(db_session)
    await svc.ensure_customer(user_id="test-user")
    await svc.credit_purchase(user_id="test-user", delta=100, reason="idemp", stripe_event_id="evt_same")
    await db_session.commit()
    # Second attempt should raise/rollback and preserve balance
    with pytest.raises(Exception):
        await svc.credit_purchase(user_id="test-user", delta=100, reason="idemp", stripe_event_id="evt_same")
        await db_session.commit()
    await db_session.rollback()


async def test_webhook_idempotency_endpoint(monkeypatch, db_session):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_x")
    app = create_app()

    # Monkeypatch webhook verification to bypass signature
    import app.api.router.webhooks as wh

    class DummyEvent(dict):
        pass

    def fake_construct_event(payload, sig_header, secret):  # type: ignore
        return DummyEvent(
            type="checkout.session.completed",
            data={"object": {"id": "cs_test_1", "customer": "cus_test_1", "metadata": {"user_id": "test-user"}}},
            id="evt_dupe",
        )

    # Also bypass SDK call to list line items
    async def fake_collect_prices(session_obj):
        return [("price_small", 1)]

    monkeypatch.setattr(wh.stripe.Webhook, "construct_event", staticmethod(fake_construct_event))
    monkeypatch.setattr(wh, "_collect_prices_from_checkout_session", fake_collect_prices)
    # Map price -> credits
    monkeypatch.setenv("STRIPE_PRICE_TO_CREDITS_JSON", json.dumps({"price_small": 50}))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # First call credits +50
        r1 = await client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1"})
        assert r1.status_code == 200
        # Second call with same event id; should be idempotent
        r2 = await client.post("/webhooks/stripe", content=b"{}", headers={"Stripe-Signature": "t=1"})
        assert r2.status_code == 200
