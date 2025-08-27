from __future__ import annotations

import argparse
import asyncio
from typing import Optional

from app.core.database import AsyncSessionLocal
from app.services.credits_service import CreditsService


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed credits for a Clerk user")
    p.add_argument("--user", "-u", dest="user", default="test-user", help="Clerk user id to seed (default: test-user)")
    p.add_argument("--delta", "-d", dest="delta", type=int, default=100, help="Credits to add (default: 100)")
    p.add_argument("--reason", "-r", dest="reason", default="seed", help="Reason label (default: seed)")
    p.add_argument("--event", dest="event", default=None, help="Optional stripe_event_id for idempotency (default: None)")
    return p.parse_args()


async def run(user: str, delta: int, reason: str, event: Optional[str]) -> int:
    async with AsyncSessionLocal() as s:
        svc = CreditsService(s)
        await svc.ensure_customer(clerk_user_id=user)
        await svc.credit_purchase(clerk_user_id=user, delta=delta, reason=reason, stripe_event_id=event)
        await s.commit()
        bal = await svc.get_balance(clerk_user_id=user)
        return int(bal)


def main() -> None:
    args = parse_args()
    balance = asyncio.run(run(args.user, args.delta, args.reason, args.event))
    print(f"Seeded {args.delta} credits for '{args.user}'. New balance: {balance}")


if __name__ == "__main__":
    main()
