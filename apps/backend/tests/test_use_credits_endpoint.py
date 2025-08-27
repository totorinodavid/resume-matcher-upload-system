import pytest
import httpx

from app.base import create_app
from app.services.credits_service import CreditsService, InsufficientCreditsError


pytestmark = pytest.mark.asyncio


async def test_use_credits_success_and_402(db_session, monkeypatch):
    monkeypatch.setenv("DISABLE_AUTH_FOR_TESTS", "1")
    app = create_app()

    # Top up balance first via service
    svc = CreditsService(db_session)
    await svc.ensure_customer(clerk_user_id="test-user")
    await svc.credit_purchase(clerk_user_id="test-user", delta=10, reason="test", stripe_event_id="evt_use_ok")
    await db_session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/use-credits", json={"units": 5, "ref": "unit-test"})
        assert resp.status_code == 200
        assert resp.json()["data"]["ok"] is True

        # Now try to spend more than remaining
        resp = await client.post("/api/v1/use-credits", json={"units": 100})
        assert resp.status_code == 402
        assert resp.json()["error"] == "Not enough credits"

