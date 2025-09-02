#!/usr/bin/env python3
"""
Comprehensive Credits System Analysis

This script performs a deep analysis of the entire credits system,
including database models, services, API endpoints, and test coverage.
"""

import sys
import os
from pathlib import Path
import json
import re
from typing import Dict, List, Any, Optional

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def analyze_database_models() -> Dict[str, Any]:
    """Analyze all credit-related database models."""
    print("🗄️  Analyzing Database Models")
    print("=" * 50)
    
    models_analysis = {
        "models_found": [],
        "relationships": [],
        "constraints": [],
        "indexes": [],
        "issues": []
    }
    
    # Check models directory
    models_dir = backend_dir / "app" / "models"
    
    if not models_dir.exists():
        models_analysis["issues"].append("Models directory not found")
        return models_analysis
    
    # Analyze credits.py
    credits_model = models_dir / "credits.py"
    if credits_model.exists():
        print("  ✅ Found credits.py")
        
        with open(credits_model, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find model classes
        model_classes = re.findall(r'class (\w+)\(.*?\):', content)
        models_analysis["models_found"].extend(model_classes)
        
        # Find relationships
        relationships = re.findall(r'relationship\("(\w+)"', content)
        models_analysis["relationships"].extend(relationships)
        
        # Find constraints
        constraints = re.findall(r'(UniqueConstraint|CheckConstraint|ForeignKey)\(([^)]+)\)', content)
        models_analysis["constraints"].extend([f"{c[0]}: {c[1]}" for c in constraints])
        
        print(f"    📋 Models: {', '.join(model_classes)}")
        print(f"    🔗 Relationships: {', '.join(relationships)}")
        print(f"    🔒 Constraints: {len(constraints)} found")
    else:
        models_analysis["issues"].append("credits.py model file not found")
    
    # Check user.py for credits_balance
    user_model = models_dir / "user.py"
    if user_model.exists():
        with open(user_model, 'r', encoding='utf-8') as f:
            user_content = f.read()
        
        if "credits_balance" in user_content:
            print("  ✅ User model has credits_balance field")
        else:
            models_analysis["issues"].append("User model missing credits_balance field")
    
    return models_analysis

def analyze_service_layer() -> Dict[str, Any]:
    """Analyze the service layer implementation."""
    print("\n🏗️  Analyzing Service Layer")
    print("=" * 50)
    
    services_analysis = {
        "services_found": [],
        "methods": {},
        "async_patterns": [],
        "issues": []
    }
    
    services_dir = backend_dir / "app" / "services"
    
    if not services_dir.exists():
        services_analysis["issues"].append("Services directory not found")
        return services_analysis
    
    # Check for credit-related services
    service_files = [
        "payment_service.py",
        "stripe_provider.py", 
        "payment_provider.py",
        "credit_service.py"
    ]
    
    for service_file in service_files:
        service_path = services_dir / service_file
        if service_path.exists():
            print(f"  ✅ Found {service_file}")
            services_analysis["services_found"].append(service_file)
            
            with open(service_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find async methods
            async_methods = re.findall(r'async def (\w+)', content)
            services_analysis["methods"][service_file] = async_methods
            services_analysis["async_patterns"].extend(async_methods)
            
            print(f"    🔄 Async methods: {len(async_methods)}")
        else:
            print(f"  ⚠️  Missing {service_file}")
    
    return services_analysis

def analyze_api_endpoints() -> Dict[str, Any]:
    """Analyze API endpoints for credits system."""
    print("\n🌐 Analyzing API Endpoints")
    print("=" * 50)
    
    api_analysis = {
        "routes_found": [],
        "endpoints": {},
        "webhooks": [],
        "issues": []
    }
    
    api_dir = backend_dir / "app" / "api" / "router"
    
    if not api_dir.exists():
        api_analysis["issues"].append("API router directory not found")
        return api_analysis
    
    # Check for credit-related routes
    route_files = list(api_dir.glob("**/*.py"))
    
    for route_file in route_files:
        if route_file.name == "__init__.py":
            continue
            
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for credit-related endpoints
        if any(term in content.lower() for term in ["credit", "payment", "stripe", "webhook"]):
            print(f"  ✅ Found credit-related routes in {route_file.name}")
            api_analysis["routes_found"].append(route_file.name)
            
            # Find endpoints
            endpoints = re.findall(r'@router\.(get|post|put|delete|patch)\("([^"]+)"', content)
            api_analysis["endpoints"][route_file.name] = endpoints
            
            # Find webhooks
            if "webhook" in content.lower():
                webhook_endpoints = re.findall(r'@router\.post\("([^"]*webhook[^"]*)"', content)
                api_analysis["webhooks"].extend(webhook_endpoints)
            
            print(f"    📍 Endpoints: {len(endpoints)}")
    
    return api_analysis

def analyze_test_coverage() -> Dict[str, Any]:
    """Analyze test coverage and structure."""
    print("\n🧪 Analyzing Test Coverage")
    print("=" * 50)
    
    test_analysis = {
        "test_files": [],
        "test_counts": {},
        "total_tests": 0,
        "coverage_areas": [],
        "issues": []
    }
    
    tests_dir = backend_dir / "tests"
    credits_tests_dir = tests_dir / "credits"
    
    if not credits_tests_dir.exists():
        test_analysis["issues"].append("Credits tests directory not found")
        return test_analysis
    
    # Analyze test files
    test_files = list(credits_tests_dir.glob("test_*.py"))
    
    for test_file in test_files:
        print(f"  ✅ Found {test_file.name}")
        test_analysis["test_files"].append(test_file.name)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count test methods
        test_methods = re.findall(r'async def test_(\w+)', content)
        test_analysis["test_counts"][test_file.name] = len(test_methods)
        test_analysis["total_tests"] += len(test_methods)
        
        # Identify coverage areas
        if "happy_path" in test_file.name:
            test_analysis["coverage_areas"].append("Happy Path")
        elif "idempotency" in test_file.name:
            test_analysis["coverage_areas"].append("Idempotency")
        elif "negative" in test_file.name:
            test_analysis["coverage_areas"].append("Error Cases")
        
        print(f"    🎯 Tests: {len(test_methods)}")
    
    return test_analysis

def analyze_configuration() -> Dict[str, Any]:
    """Analyze system configuration and environment setup."""
    print("\n⚙️  Analyzing Configuration")
    print("=" * 50)
    
    config_analysis = {
        "env_vars": {},
        "required_packages": [],
        "missing_packages": [],
        "database_config": {},
        "issues": []
    }
    
    # Check environment variables
    required_env_vars = [
        "ASYNC_DATABASE_URL",
        "SYNC_DATABASE_URL", 
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET"
    ]
    
    for env_var in required_env_vars:
        value = os.getenv(env_var)
        if value:
            # Mask sensitive values
            if "secret" in env_var.lower() or "key" in env_var.lower():
                config_analysis["env_vars"][env_var] = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                config_analysis["env_vars"][env_var] = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {env_var}: Set")
        else:
            config_analysis["env_vars"][env_var] = None
            print(f"  ⚠️  {env_var}: Not set")
    
    # Check required packages
    required_packages = [
        "pytest", "pytest-asyncio", "pytest-cov",
        "sqlalchemy", "asyncpg", "psycopg2", "stripe"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            config_analysis["required_packages"].append(package)
            print(f"  ✅ {package}: Installed")
        except ImportError:
            config_analysis["missing_packages"].append(package)
            print(f"  ❌ {package}: Missing")
    
    return config_analysis

def analyze_migrations() -> Dict[str, Any]:
    """Analyze database migration status."""
    print("\n📊 Analyzing Database Migrations")
    print("=" * 50)
    
    migration_analysis = {
        "alembic_dir": False,
        "migration_files": [],
        "latest_migration": None,
        "credits_migrations": [],
        "issues": []
    }
    
    alembic_dir = backend_dir / "alembic"
    versions_dir = alembic_dir / "versions"
    
    if alembic_dir.exists():
        migration_analysis["alembic_dir"] = True
        print("  ✅ Alembic directory found")
        
        if versions_dir.exists():
            migration_files = list(versions_dir.glob("*.py"))
            migration_analysis["migration_files"] = [f.name for f in migration_files]
            
            # Find credit-related migrations
            for migration_file in migration_files:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if any(term in content.lower() for term in ["credit", "payment", "stripe"]):
                    migration_analysis["credits_migrations"].append(migration_file.name)
                    print(f"  ✅ Credit-related migration: {migration_file.name}")
            
            if migration_files:
                latest_file = max(migration_files, key=lambda f: f.stat().st_mtime)
                migration_analysis["latest_migration"] = latest_file.name
                print(f"  📅 Latest migration: {latest_file.name}")
        else:
            migration_analysis["issues"].append("Versions directory not found")
    else:
        migration_analysis["issues"].append("Alembic directory not found")
    
    return migration_analysis

def generate_comprehensive_report() -> Dict[str, Any]:
    """Generate a comprehensive analysis report."""
    print("🔍 Comprehensive Credits System Analysis")
    print("=" * 70)
    
    # Run all analyses
    models = analyze_database_models()
    services = analyze_service_layer() 
    api = analyze_api_endpoints()
    tests = analyze_test_coverage()
    config = analyze_configuration()
    migrations = analyze_migrations()
    
    # Compile comprehensive report
    report = {
        "timestamp": "2025-09-02",
        "system_status": "ANALYSIS_COMPLETE",
        "summary": {
            "models_count": len(models["models_found"]),
            "services_count": len(services["services_found"]),
            "api_routes": len(api["routes_found"]),
            "total_tests": tests["total_tests"],
            "missing_packages": len(config["missing_packages"]),
            "credits_migrations": len(migrations["credits_migrations"])
        },
        "detailed_analysis": {
            "database_models": models,
            "service_layer": services,
            "api_endpoints": api,
            "test_coverage": tests,
            "configuration": config,
            "migrations": migrations
        },
        "readiness_score": 0,
        "recommendations": []
    }
    
    # Calculate readiness score
    score = 0
    max_score = 100
    
    # Database models (25 points)
    if len(models["models_found"]) >= 5:
        score += 25
    elif len(models["models_found"]) >= 3:
        score += 15
    
    # Service layer (20 points)
    if len(services["services_found"]) >= 3:
        score += 20
    elif len(services["services_found"]) >= 2:
        score += 10
    
    # API endpoints (15 points)
    if len(api["routes_found"]) >= 2:
        score += 15
    elif len(api["routes_found"]) >= 1:
        score += 8
    
    # Test coverage (25 points)
    if tests["total_tests"] >= 20:
        score += 25
    elif tests["total_tests"] >= 15:
        score += 20
    elif tests["total_tests"] >= 10:
        score += 15
    
    # Configuration (10 points)
    if len(config["missing_packages"]) == 0:
        score += 10
    elif len(config["missing_packages"]) <= 2:
        score += 5
    
    # Migrations (5 points)
    if len(migrations["credits_migrations"]) >= 1:
        score += 5
    
    report["readiness_score"] = score
    
    # Generate recommendations
    if score >= 90:
        report["recommendations"].append("🏆 System is production-ready!")
    elif score >= 75:
        report["recommendations"].append("✅ System is nearly production-ready")
    elif score >= 50:
        report["recommendations"].append("⚠️ System needs minor improvements")
    else:
        report["recommendations"].append("❌ System needs significant work")
    
    # Specific recommendations
    if len(config["missing_packages"]) > 0:
        report["recommendations"].append(f"Install missing packages: {', '.join(config['missing_packages'])}")
    
    if tests["total_tests"] < 20:
        report["recommendations"].append("Add more comprehensive tests")
    
    if len(models["issues"]) > 0:
        report["recommendations"].append("Fix database model issues")
    
    return report

def print_final_summary(report: Dict[str, Any]):
    """Print final analysis summary."""
    print("\n" + "="*70)
    print("🎯 FINAL ANALYSIS SUMMARY")
    print("="*70)
    
    summary = report["summary"]
    score = report["readiness_score"]
    
    print(f"📊 System Readiness Score: {score}/100")
    print(f"🗄️  Database Models: {summary['models_count']}")
    print(f"🏗️  Service Classes: {summary['services_count']}")
    print(f"🌐 API Routes: {summary['api_routes']}")
    print(f"🧪 Total Tests: {summary['total_tests']}")
    print(f"📦 Missing Packages: {summary['missing_packages']}")
    print(f"📊 Credit Migrations: {summary['credits_migrations']}")
    
    print("\n🎯 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print("\n✨ Analysis Complete!")
    
    # Test execution readiness
    config = report["detailed_analysis"]["configuration"]
    env_ready = all(config["env_vars"][var] is not None for var in ["ASYNC_DATABASE_URL", "SYNC_DATABASE_URL"])
    packages_ready = len(config["missing_packages"]) == 0
    
    if env_ready and packages_ready:
        print("\n🚀 READY FOR TEST EXECUTION!")
        print("   Run: pytest tests/credits/ -v")
    else:
        print("\n⚠️  NOT READY FOR TESTS:")
        if not env_ready:
            print("   - Set database environment variables")
        if not packages_ready:
            print("   - Install missing packages")

if __name__ == "__main__":
    try:
        report = generate_comprehensive_report()
        print_final_summary(report)
        
        # Save detailed report
        report_file = backend_dir / "CREDITS_SYSTEM_ANALYSIS.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
