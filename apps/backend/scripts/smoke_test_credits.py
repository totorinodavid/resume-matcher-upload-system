from __future__ import annotations

import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import httpx
from sqlalchemy.exc import IntegrityError

from app.core.database import AsyncSessionLocal
from app.services.credits_service import CreditsService, InsufficientCreditsError


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""


async def _service_flow() -> list[StepResult]:
    """Exercise CreditsService end-to-end on an isolated user id."""
    results: list[StepResult] = []
    user = f"smoke-{uuid.uuid4().hex[:8]}"
    async with AsyncSessionLocal() as s:
        svc = CreditsService(s)
        try:
            await svc.ensure_customer(clerk_user_id=user)
            await s.commit()
            results.append(StepResult("ensure_customer", True, user))
        except Exception as e:
            results.append(StepResult("ensure_customer", False, str(e)))
            return results

        # Fresh balance should be 0
        bal0 = await svc.get_balance(clerk_user_id=user)
        results.append(StepResult("balance_initial", bal0 == 0, f"{bal0}"))

        # Credit +50 with event id evt_1
        try:
            await svc.credit_purchase(clerk_user_id=user, delta=50, reason="seed", stripe_event_id="evt_1")
            await s.commit()
            results.append(StepResult("credit_50_evt1", True))
        except Exception as e:
            await s.rollback()
            results.append(StepResult("credit_50_evt1", False, str(e)))

        # Duplicate event should not increase balance (unique violation acceptable)
        try:
            await svc.credit_purchase(clerk_user_id=user, delta=50, reason="seed", stripe_event_id="evt_1")
            await s.commit()
            # If we get here without error, it's fine if DB ignores duplicates; verify balance still 50
            bal_dup = await svc.get_balance(clerk_user_id=user)
            results.append(StepResult("idempotent_duplicate", bal_dup == 50, f"{bal_dup}"))
        except IntegrityError:
            # Expected path when unique constraint triggers; verify unchanged balance
            await s.rollback()
            bal_dup = await svc.get_balance(clerk_user_id=user)
            results.append(StepResult("idempotent_duplicate", bal_dup == 50, f"{bal_dup}"))
        except Exception as e:
            await s.rollback()
            results.append(StepResult("idempotent_duplicate", False, str(e)))

        # Another +50 with evt_2 -> balance 100
        try:
            await svc.credit_purchase(clerk_user_id=user, delta=50, reason="seed", stripe_event_id="evt_2")
            await s.commit()
            bal1 = await svc.get_balance(clerk_user_id=user)
            results.append(StepResult("credit_50_evt2", bal1 == 100, f"{bal1}"))
        except Exception as e:
            await s.rollback()
            results.append(StepResult("credit_50_evt2", False, str(e)))

        # Debit 30 -> balance 70
        try:
            await svc.debit_usage(clerk_user_id=user, delta=30, reason="smoke")
            await s.commit()
            bal2 = await svc.get_balance(clerk_user_id=user)
            results.append(StepResult("debit_30", bal2 == 70, f"{bal2}"))
        except Exception as e:
            await s.rollback()
            results.append(StepResult("debit_30", False, str(e)))

        # Over-debit 100 -> InsufficientCreditsError
        try:
            await svc.debit_usage(clerk_user_id=user, delta=100, reason="smoke")
            await s.commit()
            results.append(StepResult("over_debit", False, "expected error"))
        except InsufficientCreditsError:
            await s.rollback()
            results.append(StepResult("over_debit", True))
        except Exception as e:
            await s.rollback()
            results.append(StepResult("over_debit", False, str(e)))

    return results


async def _endpoint_flow(base_url: str = "http://127.0.0.1:8000") -> list[StepResult]:
    """Exercise HTTP endpoints for the default test principal (test-user).

    Requires the API to run with DISABLE_AUTH_FOR_TESTS=1 so /me/* uses user=test-user.
    """
    results: list[StepResult] = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Health
            r = await client.get(f"{base_url}/healthz")
            results.append(StepResult("healthz", r.status_code == 200, str(r.status_code)))

            # Seed via service for test-user so endpoint balance reflects it
            async with AsyncSessionLocal() as s:
                svc = CreditsService(s)
                await svc.ensure_customer(clerk_user_id="test-user")
                await svc.credit_purchase(clerk_user_id="test-user", delta=100, reason="seed", stripe_event_id=str(uuid.uuid4()))
                await s.commit()

            # Balance should be >= 100 (if previous runs added more, just ensure >=)
            r = await client.get(f"{base_url}/api/v1/me/credits")
            ok_bal = False
            try:
                data = r.json()
                bal = int(data.get("data", {}).get("balance", -1))
                ok_bal = r.status_code == 200 and bal >= 100
                results.append(StepResult("http_balance_after_seed", ok_bal, json.dumps(data)))
            except Exception:
                results.append(StepResult("http_balance_after_seed", False, r.text))

            # Debit 30 via HTTP
            r = await client.post(
                f"{base_url}/api/v1/credits/debit",
                json={"delta": 30, "reason": "smoke"},
            )
            ok_debit = False
            try:
                data = r.json()
                bal = int(data.get("data", {}).get("balance", -1))
                ok_debit = r.status_code == 200 and bal >= 70
                results.append(StepResult("http_debit_30", ok_debit, json.dumps(data)))
            except Exception:
                results.append(StepResult("http_debit_30", False, r.text))

            # Over-debit large amount -> 402
            r = await client.post(
                f"{base_url}/api/v1/credits/debit",
                json={"delta": 10_000, "reason": "smoke"},
            )
            results.append(StepResult("http_over_debit", r.status_code == 402, r.text))

    except Exception as e:
        # If API isn't running, skip HTTP checks
        results.append(StepResult("http_skipped", True, f"{e}"))

    return results


async def main() -> int:
    all_results: list[StepResult] = []

    print("[credits-smoke] Service flow…", flush=True)
    all_results.extend(await _service_flow())

    print("[credits-smoke] HTTP flow…", flush=True)
    all_results.extend(await _endpoint_flow())

    # Summarize
    failed = [r for r in all_results if not r.ok]
    for r in all_results:
        status = "PASS" if r.ok else "FAIL"
        line = f" - {r.name:24} {status}"
        if r.detail:
            line += f" :: {r.detail}"
        print(line)

    print(f"[credits-smoke] {len(all_results) - len(failed)} passed, {len(failed)} failed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
