#!/usr/bin/env python3
"""
🚨 EMERGENCY RENDER DIAGNOSTICS
===============================

Backend immer noch 404 nach gunicorn fix!

MÖGLICHE PROBLEME:
1. ❌ Build failure (dependency conflicts)
2. ❌ Wrong Dockerfile/serve.py path
3. ❌ Environment variables missing
4. ❌ Render service configuration issue
5. ❌ Port binding problem

SOFORTIGE ANALYSE:
"""

import subprocess
import requests
import json
import time
from datetime import datetime

def check_project_structure():
    """Verify project structure for Render deployment"""
    print("📂 PROJECT STRUCTURE CHECK...")
    
    # Critical files for Render deployment
    critical_files = [
        "Dockerfile",
        "render.yaml", 
        "apps/backend/serve.py",
        "apps/backend/pyproject.toml",
        "apps/backend/app/main.py",
        "apps/backend/app/base.py"
    ]
    
    import os
    
    for file_path in critical_files:
        full_path = f"c:/Users/david/Documents/GitHub/Resume-Matcher/{file_path}"
        exists = os.path.exists(full_path)
        print(f"   {'✅' if exists else '❌'} {file_path}")
        
        if not exists:
            print(f"      🚨 MISSING CRITICAL FILE!")
            return False
    
    return True

def check_dockerfile_configuration():
    """Check Dockerfile configuration"""
    print("\n🐳 DOCKERFILE ANALYSIS...")
    
    try:
        with open("c:/Users/david/Documents/GitHub/Resume-Matcher/Dockerfile", 'r') as f:
            dockerfile_content = f.read()
        
        print("✅ Dockerfile exists")
        
        # Check critical elements
        checks = [
            ("FROM python:3.12-slim", "Python base image"),
            ("uv sync", "UV dependency installation"),
            ("COPY . /app", "Application copy"),
            ("EXPOSE 8000", "Port exposure")
        ]
        
        for check_str, description in checks:
            if check_str in dockerfile_content:
                print(f"   ✅ {description}: Found")
            else:
                print(f"   ❌ {description}: Missing '{check_str}'")
        
    except Exception as e:
        print(f"❌ Dockerfile check failed: {e}")

def check_render_yaml():
    """Check render.yaml configuration"""
    print("\n📋 RENDER.YAML ANALYSIS...")
    
    try:
        with open("c:/Users/david/Documents/GitHub/Resume-Matcher/render.yaml", 'r') as f:
            render_content = f.read()
        
        print("✅ render.yaml exists")
        
        # Check critical configuration
        critical_configs = [
            ("dockerfilePath: ./Dockerfile", "Dockerfile path"),
            ("dockerContext: .", "Docker context"),
            ("dockerCommand:", "Docker command"),
            ("serve.py", "Serve script"),
            ("healthCheckPath: /healthz", "Health check"),
            ("type: web", "Service type")
        ]
        
        for config, description in critical_configs:
            if config in render_content:
                print(f"   ✅ {description}: Configured")
            else:
                print(f"   ❌ {description}: Missing '{config}'")
                
        # Show docker command
        import re
        docker_cmd_match = re.search(r'dockerCommand:\s*(.+)', render_content)
        if docker_cmd_match:
            print(f"   🔧 Docker command: {docker_cmd_match.group(1)}")
        
    except Exception as e:
        print(f"❌ render.yaml check failed: {e}")

def check_pyproject_dependencies():
    """Check if all required dependencies are in pyproject.toml"""
    print("\n📦 DEPENDENCIES CHECK...")
    
    try:
        with open("c:/Users/david/Documents/GitHub/Resume-Matcher/apps/backend/pyproject.toml", 'r') as f:
            pyproject_content = f.read()
        
        print("✅ pyproject.toml exists")
        
        # Check critical dependencies
        critical_deps = [
            ("gunicorn", "Production server"),
            ("uvicorn", "ASGI server"),
            ("fastapi", "Web framework"), 
            ("stripe", "Payment processing"),
            ("sqlalchemy", "Database ORM"),
            ("psycopg", "PostgreSQL driver")
        ]
        
        missing_deps = []
        for dep, description in critical_deps:
            if dep in pyproject_content.lower():
                print(f"   ✅ {description}: {dep} found")
            else:
                print(f"   ❌ {description}: {dep} MISSING!")
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n🚨 MISSING DEPENDENCIES: {missing_deps}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ pyproject.toml check failed: {e}")
        return False

def test_alternative_render_urls():
    """Test if Render is using different URL pattern"""
    print("\n🔄 TESTING ALTERNATIVE RENDER PATTERNS...")
    
    # Render sometimes uses different URL patterns
    alternative_patterns = [
        "https://resume-matcher-backend-g7sp.onrender.com",
        "https://resume-matcher-backend.onrender.com", 
        "https://resumematcher-backend.onrender.com",
        "https://resumematcher.onrender.com",
        "https://resume-matcher.onrender.com"
    ]
    
    for url in alternative_patterns:
        print(f"\n🔍 Testing: {url}")
        
        try:
            response = requests.get(f"{url}/healthz", timeout=5)
            status = response.status_code
            print(f"   📊 Status: {status}")
            
            if status == 200:
                print(f"   🎉 FOUND WORKING URL!")
                print(f"   🔗 Active backend: {url}")
                return url
            elif status != 404:
                print(f"   ⚠️ Different response: {status}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def render_troubleshooting_guide():
    """Comprehensive troubleshooting guide"""
    print(f"\n🔧 RENDER TROUBLESHOOTING GUIDE")
    print("=" * 50)
    
    print(f"IMMEDIATE ACTIONS:")
    print(f"1. 🌐 Go to: https://dashboard.render.com")
    print(f"2. 📂 Find service: 'resume-matcher-backend-g7sp'")
    print(f"3. 📊 Check service status:")
    print(f"   - 🟢 Live = Backend running")
    print(f"   - 🟡 Building = Wait for completion")
    print(f"   - 🔴 Failed = Build error")
    print(f"   - ⚪ Sleeping = Cold start")
    
    print(f"\n📋 LOGS TO CHECK:")
    print(f"1. Click 'Logs' tab in Render dashboard")
    print(f"2. Look for recent entries")
    print(f"3. Search for these errors:")
    print(f"   - ❌ 'ModuleNotFoundError: No module named gunicorn'")
    print(f"   - ❌ 'ModuleNotFoundError: No module named stripe'")
    print(f"   - ❌ 'Failed to bind to port'")
    print(f"   - ❌ 'Database connection failed'")
    print(f"   - ✅ 'Successfully imported app.main'")
    print(f"   - ✅ 'Starting Resume Matcher Backend'")
    
    print(f"\n🚨 COMMON FIXES:")
    print(f"1. 🔄 Manual redeploy:")
    print(f"   - Render Dashboard → Deploy → Manual Deploy")
    print(f"2. 🔧 Clear build cache:")
    print(f"   - Settings → Clear build cache")
    print(f"3. ⚙️ Check environment variables:")
    print(f"   - DATABASE_URL set correctly?")
    print(f"   - All required variables present?")
    print(f"4. 📦 Verify service plan:")
    print(f"   - Free plan has limitations")
    print(f"   - Check resource usage")

def main():
    print("🚨 EMERGENCY RENDER DIAGNOSTICS")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(f"Problem: Backend returns 404 after deployment")
    
    # Check project structure
    structure_ok = check_project_structure()
    
    if structure_ok:
        # Check Dockerfile
        check_dockerfile_configuration()
        
        # Check render.yaml
        check_render_yaml()
        
        # Check dependencies
        deps_ok = check_pyproject_dependencies()
        
        # Test alternative URLs
        working_url = test_alternative_render_urls()
        
        if working_url:
            print(f"\n🎉 SOLUTION FOUND!")
            print(f"✅ Working backend URL: {working_url}")
        else:
            print(f"\n❌ NO WORKING BACKEND FOUND")
            
            if deps_ok:
                print(f"✅ Dependencies look correct")
                print(f"🔧 Problem likely in Render configuration")
            else:
                print(f"❌ Dependencies missing - rebuild needed")
    
    else:
        print(f"\n💥 PROJECT STRUCTURE ISSUES!")
        print(f"❌ Critical files missing")
    
    # Always show troubleshooting guide
    render_troubleshooting_guide()
    
    print(f"\n📞 IMMEDIATE NEXT STEPS:")
    print(f"1. Check Render dashboard logs")
    print(f"2. Look for build/runtime errors")
    print(f"3. Try manual redeploy if needed")
    print(f"4. Report findings for further assistance")

if __name__ == "__main__":
    main()
