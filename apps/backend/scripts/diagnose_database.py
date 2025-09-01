"""
Resume Matcher - Database Connection Diagnostic
Helps debug DATABASE_URL issues during Render deployment
"""
import os
import sys
from typing import Optional

def diagnose_database_config() -> dict:
    """Diagnose database configuration for Resume Matcher"""
    
    # Check all possible database environment variables
    db_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'ASYNC_DATABASE_URL': os.getenv('ASYNC_DATABASE_URL'), 
        'SYNC_DATABASE_URL': os.getenv('SYNC_DATABASE_URL'),
        'FALLBACK_DATABASE_URL': os.getenv('FALLBACK_DATABASE_URL'),
        'POSTGRES_URL': os.getenv('POSTGRES_URL'),  # Alternative naming
        'POSTGRESQL_URL': os.getenv('POSTGRESQL_URL'),  # Alternative naming
    }
    
    # Check which variables are set
    set_vars = {k: v for k, v in db_vars.items() if v}
    unset_vars = {k: v for k, v in db_vars.items() if not v}
    
    # Determine database provider from URL
    provider = "unknown"
    primary_url = None
    
    if db_vars['DATABASE_URL']:
        primary_url = db_vars['DATABASE_URL']
        if 'neon.tech' in primary_url:
            provider = "neon"
        elif 'render.com' in primary_url or 'dpg-' in primary_url:
            provider = "render"
        elif 'localhost' in primary_url:
            provider = "local"
    
    # Check Render-specific environment
    render_info = {
        'RENDER': os.getenv('RENDER'),
        'RENDER_SERVICE_ID': os.getenv('RENDER_SERVICE_ID'),
        'RENDER_SERVICE_NAME': os.getenv('RENDER_SERVICE_NAME'),
        'RENDER_EXTERNAL_URL': os.getenv('RENDER_EXTERNAL_URL'),
    }
    
    return {
        'database_vars_set': set_vars,
        'database_vars_unset': list(unset_vars.keys()),
        'primary_database_url': primary_url[:50] + "..." if primary_url else None,
        'detected_provider': provider,
        'render_environment': render_info,
        'is_render_deployment': bool(os.getenv('RENDER')),
        'environment': os.getenv('ENV', 'unknown'),
    }

def print_diagnostic():
    """Print database diagnostic information"""
    diag = diagnose_database_config()
    
    print("=" * 60)
    print("🔍 RESUME MATCHER - DATABASE DIAGNOSTIC")
    print("=" * 60)
    
    print(f"\n🌐 Environment: {diag['environment']}")
    print(f"📍 Render Deployment: {diag['is_render_deployment']}")
    print(f"🗃️ Detected Provider: {diag['detected_provider']}")
    
    if diag['primary_database_url']:
        print(f"✅ Primary Database URL: {diag['primary_database_url']}")
    else:
        print("❌ No PRIMARY DATABASE_URL found!")
    
    print(f"\n📊 Database Variables Set ({len(diag['database_vars_set'])}):")
    for var, value in diag['database_vars_set'].items():
        masked_value = value[:20] + "..." if len(value) > 20 else value
        print(f"   ✅ {var}: {masked_value}")
    
    print(f"\n❌ Database Variables Missing ({len(diag['database_vars_unset'])}):")
    for var in diag['database_vars_unset']:
        print(f"   ❌ {var}")
    
    print(f"\n🔧 Render Environment:")
    for var, value in diag['render_environment'].items():
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if not diag['database_vars_set']:
        print("   🚨 CRITICAL: No database URL configured!")
        print("   📝 Action: Create PostgreSQL database in Render dashboard")
        print("   📝 Ensure database name matches 'resume-matcher-db' in render.yaml")
    
    elif diag['detected_provider'] == 'neon':
        print("   ⚠️  WARNING: Still using Neon database")
        print("   📝 Action: Database migration to Render not complete")
        print("   📝 Check: Render PostgreSQL database creation status")
    
    elif diag['detected_provider'] == 'render':
        print("   ✅ SUCCESS: Using Render PostgreSQL")
        print("   📝 Ready: Database configuration looks correct")
    
    else:
        print("   ⚠️  WARNING: Unknown database provider")
        print("   📝 Action: Verify DATABASE_URL format")
    
    print("=" * 60)

if __name__ == "__main__":
    print_diagnostic()
