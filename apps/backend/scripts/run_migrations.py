"""Run Alembic migrations to head using environment configuration.

This script is a thin wrapper around Alembic's CLI to make it easy to
programmatically invoke migrations in container platforms (Render, Railway)
or locally. It resolves `ALEMBIC_CONFIG` or defaults to the backend's
alembic.ini and relies on `DATABASE_URL` (or settings) as configured in
alembic/env.py.
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    # Ensure we run from repo root or any location; construct -c path explicitly
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    default_ini = os.path.join(backend_dir, "alembic.ini")
    alembic_ini = os.getenv("ALEMBIC_CONFIG", default_ini)

    # Defer import to avoid alembic dependency when unused
    try:
        from alembic.config import main as alembic_main  # type: ignore
    except Exception as e:  # pragma: no cover
        print(f"Failed to import Alembic: {e}", file=sys.stderr)
        return 1

    # Build argv: alembic -c <ini> upgrade head
    argv = [
        "alembic",
        "-c",
        alembic_ini,
        "upgrade",
        "head",
    ]
    try:
        # Exit with Alembic's SystemExit code
        raise SystemExit(alembic_main(argv))
    except SystemExit as se:
        return int(se.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
