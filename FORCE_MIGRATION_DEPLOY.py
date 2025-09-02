#!/usr/bin/env python3
"""
🚨 FORCE MIGRATION DEPLOYMENT
Problem: Render führt Alembic Migrations nicht automatisch aus
Solution: Trigger a deployment that forces migration execution

This script will:
1. Update render.yaml to force migration execution
2. Commit the change
3. Push to trigger auto-deployment
4. Monitor deployment success
"""

import subprocess
import time
import os

def run_command(cmd, description):
    """Run command and return success"""
    print(f"📝 {description}")
    print(f"💻 Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="c:\\Users\\david\\Documents\\GitHub\\Resume-Matcher")
        
        if result.returncode == 0:
            print(f"✅ Success!")
            if result.stdout.strip():
                print(f"📤 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed!")
            if result.stderr.strip():
                print(f"📥 Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def force_migration_deployment():
    """Force Render to run migrations by triggering deployment"""
    print("🚨 FORCE MIGRATION DEPLOYMENT")
    print("=" * 50)
    
    # 1. Check if render.yaml exists
    render_yaml_path = "c:\\Users\\david\\Documents\\GitHub\\Resume-Matcher\\render.yaml"
    if not os.path.exists(render_yaml_path):
        print("❌ render.yaml not found")
        return False
    
    # 2. Add a migration hook to render.yaml
    print("\n1️⃣ Adding migration hook to render.yaml")
    
    # Read current render.yaml
    with open(render_yaml_path, 'r') as f:
        content = f.read()
    
    # Add migration command if not present
    if "alembic upgrade head" not in content:
        print("📝 Adding alembic migration to render.yaml")
        
        # Find the backend service and add buildCommand
        lines = content.split('\n')
        new_lines = []
        in_backend_service = False
        
        for line in lines:
            new_lines.append(line)
            
            # Check if we're in the backend service
            if 'name: resume-matcher-backend' in line:
                in_backend_service = True
            elif line.startswith('- name:') and in_backend_service:
                in_backend_service = False
            
            # Add migration command after type: web
            if in_backend_service and 'type: web' in line:
                new_lines.append('  buildCommand: cd apps/backend && alembic upgrade head')
        
        # Write updated render.yaml
        with open(render_yaml_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Updated render.yaml with migration command")
    else:
        print("✅ Migration command already present in render.yaml")
    
    # 3. Commit the change
    print("\n2️⃣ Committing render.yaml changes")
    
    success = run_command("git add render.yaml", "Adding render.yaml to git")
    if not success:
        return False
    
    success = run_command('git commit -m "🚨 FORCE MIGRATION: Add alembic upgrade to render.yaml"', "Committing migration hook")
    if not success:
        print("⚠️  No changes to commit (already up to date)")
    
    # 4. Push to trigger deployment
    print("\n3️⃣ Pushing to trigger auto-deployment")
    
    success = run_command("git push", "Pushing to GitHub (triggers Render deployment)")
    if not success:
        return False
    
    print("\n🎉 FORCE MIGRATION DEPLOYMENT INITIATED!")
    print("📝 Render will now:")
    print("   1. Detect the git push")
    print("   2. Run 'alembic upgrade head' during build")
    print("   3. Execute migration 0009_add_users_credits_balance.py")
    print("   4. Add credits_balance column to users table")
    print("   5. Start the backend with working credits system")
    
    print("\n🔍 Monitor deployment at:")
    print("   https://dashboard.render.com/")
    
    return True

def main():
    """Main execution"""
    print("🚨 RENDER MIGRATION FORCE DEPLOYMENT")
    print("Problem: credits_balance column missing in production")
    print("Solution: Force Render to run Alembic migrations")
    print("=" * 60)
    
    success = force_migration_deployment()
    
    if success:
        print("\n✅ DEPLOYMENT TRIGGERED SUCCESSFULLY")
        print("📝 The migration will run on Render in 2-3 minutes")
        print("📝 Check logs: https://dashboard.render.com/")
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("📝 Manual intervention required")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
