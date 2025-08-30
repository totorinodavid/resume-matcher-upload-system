import asyncio
from app.core.database import AsyncSessionLocal
from app.services.credits_service import CreditsService

async def main():
    async with AsyncSessionLocal() as s:
        svc = CreditsService(s)
        b = await svc.get_balance(user_id="test-user")
        print("balance:", b)

asyncio.run(main())
