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
    
    # CRITICAL: Check DATABASE_URL immediately
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        print("❌ CRITICAL: No DATABASE_URL found!")
        print("🔧 Available environment variables:")
        for key in sorted(os.environ.keys()):
            if 'DATABASE' in key or 'POSTGRES' in key or 'DB' in key:
                value = os.environ[key]
                masked = value[:30] + "..." if len(value) > 30 else value
                print(f"   {key}: {masked}")
        
        # Try to find alternative database URLs
        alternatives = [
            'ASYNC_DATABASE_URL',
            'SYNC_DATABASE_URL', 
            'FALLBACK_DATABASE_URL',
            'MANUAL_DATABASE_URL',  # Emergency manual override
            'POSTGRES_URL',
            'POSTGRESQL_URL'
        ]
        
        for alt in alternatives:
            alt_url = os.getenv(alt, "").strip()
            if alt_url:
                print(f"🔄 Found alternative: {alt}")
                os.environ["DATABASE_URL"] = alt_url
                print(f"✅ Set DATABASE_URL to: {alt_url[:30]}...")
                break
        else:
            print("💥 No database URL found! Backend will fail to start.")
            print("🚨 Check Render Dashboard: PostgreSQL database 'resume-matcher-db' exists?")
            return False
    else:
        if 'neon.tech' in db_url:
            print(f"⚠️ WARNING: Still using Neon database!")
            print(f"   DATABASE_URL: {db_url[:50]}...")
            print(f"🔧 Expected: Render PostgreSQL URL (dpg-xxxxx)")
        elif 'render.com' in db_url or 'dpg-' in db_url:
            print(f"✅ SUCCESS: Using Render PostgreSQL!")
            print(f"   DATABASE_URL: {db_url[:50]}...")
        else:
            print(f"❓ Unknown database provider:")
            print(f"   DATABASE_URL: {db_url[:50]}...")
    
    return True

# Import the ASGI app after path fix
from app.main import app  # noqa: E402


def main() -> None:
    # Run diagnostic first
    print("\n🔍 Running database diagnostic...")
    db_check_passed = run_database_diagnostic()
    
    if not db_check_passed:
        print("💥 Database configuration failed. Exiting...")
        sys.exit(1)
    
    print("\n🚀 Starting Resume Matcher Backend...")
    
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8000"))
    # Disable reload in production
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
