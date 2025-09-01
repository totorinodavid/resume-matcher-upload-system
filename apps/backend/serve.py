"""Robust Uvicorn entrypoint for Render.

Ensures sys.path includes the backend root so the `app` package resolves
reliably, then starts Uvicorn programmatically.
"""
from __future__ import annotations

import os
import sys
import uvicorn

# Ensure /app/apps/backend is on sys.path
BACKEND_ROOT = os.path.abspath(os.path.dirname(__file__))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

def run_database_diagnostic():
    """Run database diagnostic before starting server"""
    try:
        from scripts.diagnose_database import print_diagnostic
        print_diagnostic()
    except Exception as e:
        print(f"⚠️ Database diagnostic failed: {e}")

# Import the ASGI app after path fix
from app.main import app  # noqa: E402


def main() -> None:
    # Run diagnostic first
    print("\n🔍 Running database diagnostic...")
    run_database_diagnostic()
    print("\n🚀 Starting Resume Matcher Backend...")
    
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8000"))
    # Disable reload in production
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
