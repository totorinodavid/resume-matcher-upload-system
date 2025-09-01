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

def check_database_url_before_import():
    """CRITICAL: Check DATABASE_URL before importing app.main to prevent startup failure"""
    print("\n🔍 PRE-IMPORT DATABASE CHECK...")
    
    # Check for any database URL
    db_url = os.getenv("DATABASE_URL", "").strip()
    
    if not db_url:
        print("❌ CRITICAL: No DATABASE_URL found!")
        print("🔧 Available environment variables:")
        
        db_vars = {}
        for key in sorted(os.environ.keys()):
            if any(word in key.upper() for word in ['DATABASE', 'POSTGRES', 'DB_']):
                value = os.environ[key]
                masked = value[:30] + "..." if len(value) > 30 else value
                db_vars[key] = masked
                print(f"   {key}: {masked}")
        
        if not db_vars:
            print("   ❌ No database-related environment variables found!")
        
        # Try to find alternative database URLs and set DATABASE_URL
        alternatives = [
            'ASYNC_DATABASE_URL',
            'SYNC_DATABASE_URL', 
            'FALLBACK_DATABASE_URL',
            'MANUAL_DATABASE_URL',
            'POSTGRES_URL',
            'POSTGRESQL_URL'
        ]
        
        for alt in alternatives:
            alt_url = os.getenv(alt, "").strip()
            if alt_url:
                print(f"🔄 Found alternative: {alt}")
                os.environ["DATABASE_URL"] = alt_url
                print(f"✅ Set DATABASE_URL to: {alt_url[:30]}...")
                return True
        
        # If still no database URL, create a temporary one to prevent startup crash
        print("⚠️ No database URL found! Creating temporary LOCAL fallback...")
        print("🚨 THIS WILL FAIL IN PRODUCTION - CHECK RENDER POSTGRESQL SETUP!")
        fallback_url = "postgresql+asyncpg://postgres:password@localhost:5432/resume_matcher"
        os.environ["DATABASE_URL"] = fallback_url
        print(f"🔧 Temporary DATABASE_URL: {fallback_url}")
        return False
    
    else:
        if 'neon.tech' in db_url:
            print(f"⚠️ WARNING: Still using Neon database!")
            print(f"   DATABASE_URL: {db_url[:50]}...")
            print(f"🔧 Expected: Render PostgreSQL URL (dpg-xxxxx)")
            print(f"🚨 THIS EXPLAINS THE QUOTA ERROR!")
        elif 'render.com' in db_url or 'dpg-' in db_url:
            print(f"✅ SUCCESS: Using Render PostgreSQL!")
            print(f"   DATABASE_URL: {db_url[:50]}...")
        else:
            print(f"❓ Unknown database provider:")
            print(f"   DATABASE_URL: {db_url[:50]}...")
        
        return True

def run_database_diagnostic():
    """Run database diagnostic before starting server"""
    try:
        from scripts.diagnose_database import print_diagnostic
        print_diagnostic()
    except Exception as e:
        print(f"⚠️ Database diagnostic failed: {e}")
    
    return True

# CRITICAL: Check database URL BEFORE importing app.main
database_ok = check_database_url_before_import()

# Import the ASGI app after database URL check
print("📦 Importing app.main...")
try:
    from app.main import app  # noqa: E402
    print("✅ Successfully imported app.main")
except Exception as e:
    print(f"💥 Failed to import app.main: {e}")
    print("🚨 This is likely due to database connection issues during import")
    sys.exit(1)


def main() -> None:
    # Run diagnostic (detailed analysis)
    print("\n🔍 Running detailed database diagnostic...")
    db_check_passed = run_database_diagnostic()
    
    if not database_ok and not db_check_passed:
        print("💥 Database configuration failed. Exiting...")
        sys.exit(1)
    
    print("\n🚀 Starting Resume Matcher Backend...")
    
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8000"))
    # Disable reload in production
    uvicorn.run(app, host=host, port=port, log_level=os.getenv("LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
