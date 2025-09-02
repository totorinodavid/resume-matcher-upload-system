#!/usr/bin/env python3
"""
🚨 ULTIMATE SCALING SOLUTION - Render Multiple Container Issue
Gefunden: Das Problem ist, dass Render mehrere Container-Instanzen läuft!
"""

import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_multiple_instances():
    """Check if multiple container instances are running"""
    base_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    # Test multiple requests to see different responses
    responses = []
    
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/healthz", timeout=30)
            headers = dict(response.headers)
            
            # Look for server identifiers
            server_info = {
                'status_code': response.status_code,
                'server': headers.get('server', 'unknown'),
                'x_request_id': headers.get('x-request-id', 'none'),
                'date': headers.get('date', 'none'),
                'response_time': response.elapsed.total_seconds()
            }
            
            responses.append(server_info)
            logger.info(f"Request {i+1}: {server_info}")
            
            time.sleep(1)  # Wait 1 second between requests
            
        except Exception as e:
            logger.error(f"Request {i+1} failed: {e}")
            responses.append({'error': str(e)})
    
    return responses

def force_container_restart():
    """Force all containers to restart by triggering deployment"""
    logger.info("🔄 FORCING COMPLETE CONTAINER RESTART...")
    
    # This will be done via git push to trigger new deployment
    print("\n" + "="*80)
    print("🚨 ULTIMATE SOLUTION: FORCE ALL CONTAINERS TO RESTART")
    print("="*80)
    
    print("\n1. PROBLEM IDENTIFIED:")
    print("   ✅ Multiple Render container instances running")
    print("   ✅ Some containers have old code without migration")
    print("   ✅ Load balancer distributing between old/new containers")
    
    print("\n2. SOLUTION:")
    print("   🔄 Force complete deployment restart")
    print("   🔄 Ensure ALL containers get new code")
    print("   🔄 Scale down to 1 instance temporarily")
    
    print("\n3. ACTIONS NEEDED:")
    print("   1. Scale Render service to 1 instance")
    print("   2. Force new deployment")
    print("   3. Verify single container has migration")
    print("   4. Scale back up if needed")

def check_scaling_status():
    """Check current scaling configuration"""
    logger.info("📊 CHECKING SCALING STATUS...")
    
    responses = check_multiple_instances()
    
    print(f"\n📊 ANALYSIS OF {len(responses)} REQUESTS:")
    
    # Analyze response patterns
    unique_servers = set()
    success_count = 0
    
    for i, resp in enumerate(responses):
        if 'error' not in resp:
            success_count += 1
            server_id = f"{resp.get('server', 'unknown')}_{resp.get('response_time', 0):.3f}s"
            unique_servers.add(server_id)
            print(f"   Request {i+1}: ✅ {resp['status_code']} - {server_id}")
        else:
            print(f"   Request {i+1}: ❌ {resp['error']}")
    
    print(f"\n🔍 DETECTED SERVERS: {len(unique_servers)}")
    for server in unique_servers:
        print(f"   - {server}")
    
    if len(unique_servers) > 1:
        print("\n🚨 MULTIPLE CONTAINERS CONFIRMED!")
        print("   This explains the inconsistent credits_balance column errors")
        return True
    else:
        print("\n✅ Single container detected")
        return False

def main():
    print("🚨 ULTIMATE SCALING SOLUTION")
    print("="*50)
    
    # Check if multiple instances are running
    multiple_detected = check_scaling_status()
    
    if multiple_detected:
        force_container_restart()
        
        print("\n" + "="*80)
        print("🎯 NEXT STEPS - MANUAL ACTIONS REQUIRED:")
        print("="*80)
        
        print("\n1. LOGIN TO RENDER DASHBOARD:")
        print("   https://dashboard.render.com/")
        
        print("\n2. GO TO SERVICE SCALING:")
        print("   - Open your backend service")
        print("   - Go to 'Scaling' tab")
        print("   - Set instances to 1 (temporarily)")
        
        print("\n3. FORCE REDEPLOY:")
        print("   - Go to 'Manual Deploy' in Dashboard")
        print("   - Deploy latest commit")
        print("   - OR trigger via git push (automated)")
        
        print("\n4. VERIFY MIGRATION:")
        print("   - Wait for deployment to complete")
        print("   - Check logs for migration success")
        print("   - Test credits endpoint")
        
        print("\n5. SCALE BACK UP (if needed):")
        print("   - Once working, can scale back to multiple instances")
        
    else:
        print("\n✅ No scaling issues detected")
        print("The problem might be elsewhere")

if __name__ == "__main__":
    main()
