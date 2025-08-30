import asyncio
import pytest
import httpx

from app.base import create_app
from app.services.credits_service import CreditsService


pytestmark = pytest.mark.asyncio


async def test_parallel_debits_one_wins_one_402(db_session, monkeypatch):
    monkeypatch.setenv("DISABLE_AUTH_FOR_TESTS", "1")
    app = create_app()

    svc = CreditsService(db_session)
    await svc.ensure_customer(user_id="test-user")
    await svc.credit_purchase(user_id="test-user", delta=1, reason="race", stripe_event_id="evt_race")
    await db_session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async def spend_one():
            return await client.post("/api/v1/use-credits", json={"units": 1, "ref": "race"})

        r1, r2 = await asyncio.gather(spend_one(), spend_one())
        codes = sorted([r1.status_code, r2.status_code])
        assert codes == [200, 402]
