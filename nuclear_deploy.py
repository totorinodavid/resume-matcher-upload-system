#!/usr/bin/env python3
"""
Nuclear Deployment Script
Forces complete cache invalidation and deployment
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    print(f"🔥 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e.stderr}")
        return False

def nuclear_deploy():
    timestamp = int(time.time())
    
    print(f"🚀 NUCLEAR DEPLOYMENT INITIATED - {timestamp}")
    print("This will force complete container rebuild and cache invalidation")
    
    # Step 1: Commit nuclear files
    if not run_command("git add .", "Adding nuclear files to git"):
        return False
    
    commit_msg = f"NUCLEAR REBUILD: Force cache bust {timestamp}"
    if not run_command(f'git commit -m "{commit_msg}"', "Committing nuclear changes"):
        print("⚠️ No changes to commit or commit failed")
    
    # Step 2: Push to trigger deployment
    if not run_command("git push origin main", "Pushing nuclear deployment"):
        return False
    
    print(f"✅ NUCLEAR DEPLOYMENT TRIGGERED - {timestamp}")
    print("🔥 Complete container cache invalidation initiated")
    print("⏳ Monitor Render dashboard for deployment progress")
    print("💡 This should resolve the 'column does not exist' issue permanently")
    
    return True

if __name__ == "__main__":
    nuclear_deploy()
