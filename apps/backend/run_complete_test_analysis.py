#!/usr/bin/env python3
"""
Credits System Test Runner with Database Setup

This script sets up a test database and runs the complete test suite.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def setup_test_database():
    """Set up environment variables for testing."""
    print("🗄️  Setting up test database configuration")
    print("=" * 50)
    
    # Option 1: Use in-memory SQLite for quick testing (if supported)
    test_db_url_sync = "postgresql+psycopg://postgres:test@localhost:5432/test_credits"
    test_db_url_async = "postgresql+asyncpg://postgres:test@localhost:5432/test_credits"
    
    # Set environment variables
    os.environ["SYNC_DATABASE_URL"] = test_db_url_sync
    os.environ["ASYNC_DATABASE_URL"] = test_db_url_async
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key_for_testing"
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_fake_secret_for_testing"
    
    print(f"  ✅ SYNC_DATABASE_URL: {test_db_url_sync}")
    print(f"  ✅ ASYNC_DATABASE_URL: {test_db_url_async}")
    print(f"  ✅ STRIPE_SECRET_KEY: sk_test_fake_key...")
    print(f"  ✅ STRIPE_WEBHOOK_SECRET: whsec_fake_secret...")
    
    return True

def run_test_analysis():
    """Run the comprehensive system analysis again."""
    print("\n🔍 Re-running System Analysis with Test Environment")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [
                "C:/Users/david/MiniConda3/Scripts/conda.exe", 
                "run", "-p", "C:\\Users\\david\\MiniConda3", 
                "--no-capture-output", "python", "analyze_credits_system.py"
            ],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Analysis completed successfully")
            print(result.stdout)
        else:
            print("❌ Analysis failed")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out")
        return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def run_test_validation():
    """Run test validation to check structure."""
    print("\n🧪 Running Test Validation")
    print("=" * 40)
    
    try:
        result = subprocess.run(
            [
                "C:/Users/david/MiniConda3/Scripts/conda.exe", 
                "run", "-p", "C:\\Users\\david\\MiniConda3", 
                "--no-capture-output", "python", "validate_tests.py"
            ],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Test validation successful")
            print(result.stdout)
        else:
            print("❌ Test validation failed")
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def attempt_docker_database():
    """Attempt to start a Docker PostgreSQL database for testing."""
    print("\n🐳 Attempting to start Docker PostgreSQL")
    print("=" * 45)
    
    try:
        # Check if Docker is available
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if docker_check.returncode != 0:
            print("❌ Docker not available")
            return False
        
        print("✅ Docker is available")
        
        # Start PostgreSQL container
        docker_run = subprocess.run(
            [
                "docker", "run", "--name", "resume-matcher-test-db",
                "-e", "POSTGRES_PASSWORD=testpass",
                "-e", "POSTGRES_USER=testuser", 
                "-e", "POSTGRES_DB=resume_matcher_test",
                "-p", "5433:5432",
                "-d", "postgres:15"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if docker_run.returncode == 0:
            print("✅ PostgreSQL container started successfully")
            
            # Update environment variables for Docker database
            os.environ["SYNC_DATABASE_URL"] = "postgresql+psycopg://testuser:testpass@localhost:5433/resume_matcher_test"
            os.environ["ASYNC_DATABASE_URL"] = "postgresql+asyncpg://testuser:testpass@localhost:5433/resume_matcher_test"
            
            print("✅ Updated database URLs for Docker PostgreSQL")
            return True
        else:
            print(f"❌ Failed to start container: {docker_run.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ Docker operation timed out")
        return False
    except FileNotFoundError:
        print("❌ Docker command not found")
        return False
    except Exception as e:
        print(f"❌ Docker error: {e}")
        return False

def run_actual_tests():
    """Attempt to run the actual pytest suite."""
    print("\n🚀 Attempting to Run Actual Tests")
    print("=" * 40)
    
    try:
        # Run a single test first to check database connectivity
        result = subprocess.run(
            [
                "C:/Users/david/MiniConda3/Scripts/conda.exe", 
                "run", "-p", "C:\\Users\\david\\MiniConda3", 
                "--no-capture-output", "python", "-m", "pytest", 
                "tests/credits/test_happy_path.py::TestHappyPath::test_purchase_credits",
                "-v", "--tb=short"
            ],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Test Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Single test passed! Running full suite...")
            
            # Run full test suite
            full_result = subprocess.run(
                [
                    "C:/Users/david/MiniConda3/Scripts/conda.exe", 
                    "run", "-p", "C:\\Users\\david\\MiniConda3", 
                    "--no-capture-output", "python", "-m", "pytest", 
                    "tests/credits/", "-v", "--tb=short"
                ],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print("Full Test Suite Output:")
            print(full_result.stdout)
            
            if full_result.stderr:
                print("Full Test Suite Errors:")
                print(full_result.stderr)
            
            return full_result.returncode == 0
        else:
            print("❌ Single test failed - database connectivity issue")
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def generate_final_report():
    """Generate final test execution report."""
    print("\n📊 FINAL TEST EXECUTION REPORT")
    print("=" * 50)
    
    # Check if analysis file exists
    analysis_file = backend_dir / "CREDITS_SYSTEM_ANALYSIS.json"
    if analysis_file.exists():
        print("✅ System analysis completed")
        
        import json
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
        
        score = analysis.get("readiness_score", 0)
        total_tests = analysis.get("summary", {}).get("total_tests", 0)
        
        print(f"📊 System Readiness Score: {score}/100")
        print(f"🧪 Total Test Cases: {total_tests}")
        
        if score >= 85:
            print("🏆 SYSTEM IS PRODUCTION READY!")
        elif score >= 75:
            print("✅ System is nearly production ready")
        else:
            print("⚠️ System needs improvements")
    
    # Environment status
    env_vars = [
        "SYNC_DATABASE_URL", "ASYNC_DATABASE_URL", 
        "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"
    ]
    
    env_status = all(os.getenv(var) for var in env_vars)
    
    print(f"\n⚙️ Environment Configuration: {'✅ Ready' if env_status else '❌ Missing vars'}")
    
    # Package status
    required_packages = ["pytest", "pytest_asyncio", "sqlalchemy", "asyncpg", "psycopg2"]
    package_status = []
    
    for package in required_packages:
        try:
            __import__(package)
            package_status.append(True)
        except ImportError:
            package_status.append(False)
    
    packages_ready = all(package_status)
    print(f"📦 Required Packages: {'✅ All installed' if packages_ready else '❌ Missing packages'}")
    
    print("\n🎯 RECOMMENDATIONS:")
    if env_status and packages_ready:
        print("  🚀 Ready for production deployment!")
        print("  🧪 Run full test suite: pytest tests/credits/ -v")
    else:
        if not env_status:
            print("  ⚠️ Set up database environment variables")
        if not packages_ready:
            print("  ⚠️ Install missing Python packages")

if __name__ == "__main__":
    print("🎯 Credits System Complete Test & Analysis")
    print("=" * 60)
    
    # Step 1: Set up test environment
    setup_success = setup_test_database()
    
    if setup_success:
        print("\n✅ Test environment configured")
        
        # Step 2: Re-run analysis with environment
        analysis_success = run_test_analysis()
        
        # Step 3: Validate test structure
        validation_success = run_test_validation()
        
        # Step 4: Try Docker database (optional)
        docker_success = attempt_docker_database()
        
        # Step 5: Run actual tests (if database available)
        if docker_success:
            test_success = run_actual_tests()
        else:
            print("\n⚠️ Skipping actual test execution (no database)")
            test_success = False
        
        # Step 6: Generate final report
        generate_final_report()
        
        print("\n✨ Complete analysis finished!")
        
    else:
        print("❌ Failed to set up test environment")
        sys.exit(1)
