"""Start the API locally with auth bypass for tests.

This ensures DISABLE_AUTH_FOR_TESTS=1 is set inside the Python process,
so routes depending on require_auth are overridden for local smoke tests.
"""
from __future__ import annotations

import os
import sys

import uvicorn


def main() -> None:
    # Ensure backend root is on sys.path so `app` package resolves reliably
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    # Force auth bypass for this process
    os.environ["DISABLE_AUTH_FOR_TESTS"] = "1"

    # Start the ASGI app
    uvicorn.run("app.main:app", host="127.0.0.1", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
