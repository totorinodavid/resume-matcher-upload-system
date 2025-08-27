from __future__ import annotations

import argparse
import hmac
import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

import requests


def build_signature_header(secret: str, payload: bytes, timestamp: Optional[int] = None) -> str:
    ts = int(timestamp or time.time())
    signed_payload = f"{ts}.".encode("utf-8") + payload
    digest = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    # Stripe supports multiple signatures; we send a single v1
    return f"t={ts},v1={digest}"


def default_event_payload(
    event_type: str,
    *,
    credits: int = 100,
    clerk_user_id: Optional[str] = None,
    stripe_customer_id: Optional[str] = None,
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    if event_type not in {"checkout.session.completed", "invoice.paid"}:
        raise ValueError("Unsupported event type for test payload")

    obj: Dict[str, Any] = {
        "id": event_id or f"evt_test_{int(time.time())}",
        "object": "event",
        "type": event_type,
        "data": {
            "object": {
                "object": "checkout.session" if event_type == "checkout.session.completed" else "invoice",
                "customer": stripe_customer_id or "cus_test_123",
                "metadata": {
                    "credits": str(int(credits)),
                    **({"clerk_user_id": clerk_user_id} if clerk_user_id else {}),
                },
            }
        },
    }
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a signed test Stripe webhook to your backend")
    parser.add_argument("--url", required=True, help="Webhook endpoint URL, e.g. https://<render-app>/webhooks/stripe")
    parser.add_argument("--type", default="checkout.session.completed", help="Event type (default: checkout.session.completed)")
    parser.add_argument("--credits", type=int, default=100, help="Credits to include in metadata (default: 100)")
    parser.add_argument("--clerk", default=None, help="Clerk user id to include in metadata")
    parser.add_argument("--customer", default=None, help="Stripe customer id to include")
    parser.add_argument("--event-id", default=None, help="Explicit event id (optional)")
    parser.add_argument(
        "--secret",
        default=os.getenv("STRIPE_WEBHOOK_SECRET"),
        help="Webhook signing secret (defaults to STRIPE_WEBHOOK_SECRET env)",
    )
    args = parser.parse_args()

    if not args.secret:
        raise SystemExit("Missing STRIPE_WEBHOOK_SECRET (pass --secret or set env)")

    payload_obj = default_event_payload(
        args.type,
        credits=args.credits,
        clerk_user_id=args.clerk,
        stripe_customer_id=args.customer,
        event_id=args.event_id,
    )
    payload_bytes = json.dumps(payload_obj).encode("utf-8")
    sig_header = build_signature_header(args.secret, payload_bytes)

    resp = requests.post(
        args.url,
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "Stripe-Signature": sig_header,
        },
        timeout=15,
    )
    print(f"Status: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()
