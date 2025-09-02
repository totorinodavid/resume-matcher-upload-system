#!/usr/bin/env python3
"""
Validation script for the credits test suite.

Checks that all test files are properly structured and importable.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def validate_test_structure():
    """Validate that all test files are properly structured."""
    print("🧪 Validating Credits Test Suite Structure")
    print("=" * 50)
    
    # Check test directory structure
    tests_dir = backend_dir / "tests"
    credits_dir = tests_dir / "credits"
    
    expected_files = [
        tests_dir / "conftest.py",
        tests_dir / "README.md", 
        credits_dir / "__init__.py",
        credits_dir / "test_happy_path.py",
        credits_dir / "test_idempotency.py",
        credits_dir / "test_negative_cases.py"
    ]
    
    print("📁 Checking file structure:")
    for file_path in expected_files:
        if file_path.exists():
            print(f"  ✅ {file_path.relative_to(backend_dir)}")
        else:
            print(f"  ❌ {file_path.relative_to(backend_dir)} (missing)")
    
    # Check test imports
    print("\n📦 Checking test imports:")
    
    try:
        # Basic imports that should work without database
        import pytest
        print("  ✅ pytest")
    except ImportError as e:
        print(f"  ❌ pytest: {e}")
    
    try:
        import pytest_asyncio
        print("  ✅ pytest_asyncio")
    except ImportError as e:
        print(f"  ❌ pytest_asyncio: {e}")
    
    try:
        from sqlalchemy import text
        print("  ✅ sqlalchemy")
    except ImportError as e:
        print(f"  ❌ sqlalchemy: {e}")
    
    try:
        from uuid import uuid4
        test_uuid = str(uuid4())
        assert len(test_uuid) == 36
        print("  ✅ uuid4 generation")
    except Exception as e:
        print(f"  ❌ uuid4 generation: {e}")
    
    # Check test file syntax
    print("\n🔍 Checking test file syntax:")
    
    test_files = [
        credits_dir / "test_happy_path.py",
        credits_dir / "test_idempotency.py", 
        credits_dir / "test_negative_cases.py"
    ]
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic syntax check
            compile(content, str(test_file), 'exec')
            
            # Check for required elements
            has_class = "class Test" in content
            has_async_test = "@pytest_asyncio.async_test" in content
            has_assertions = "assert " in content
            
            status = "✅" if all([has_class, has_async_test, has_assertions]) else "⚠️"
            print(f"  {status} {test_file.name}")
            
            if not has_class:
                print(f"    - Missing test class")
            if not has_async_test:
                print(f"    - Missing async test decorators")
            if not has_assertions:
                print(f"    - Missing assertions")
                
        except SyntaxError as e:
            print(f"  ❌ {test_file.name}: Syntax error - {e}")
        except Exception as e:
            print(f"  ❌ {test_file.name}: {e}")
    
    # Count test methods
    print("\n📊 Test Coverage Summary:")
    
    test_counts = {}
    total_tests = 0
    
    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count test methods
            test_methods = content.count("async def test_")
            test_counts[test_file.name] = test_methods
            total_tests += test_methods
            
        except Exception:
            test_counts[test_file.name] = 0
    
    for filename, count in test_counts.items():
        print(f"  📋 {filename}: {count} tests")
    
    print(f"\n🎯 Total Tests: {total_tests}")
    
    # Check README
    readme_path = tests_dir / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            has_setup = "Environment Setup" in readme_content
            has_commands = "pytest tests/credits/" in readme_content
            has_schema = "Database Schema" in readme_content
            
            readme_score = sum([has_setup, has_commands, has_schema])
            print(f"\n📚 README.md: {readme_score}/3 sections present")
            
        except Exception as e:
            print(f"\n📚 README.md: Error reading - {e}")
    
    print("\n✨ Validation Complete!")
    print("\n🚀 To run tests (after setting up database):")
    print("   export ASYNC_DATABASE_URL='postgresql+asyncpg://...'")
    print("   export SYNC_DATABASE_URL='postgresql+psycopg://...'")
    print("   pytest tests/credits/ -v")

if __name__ == "__main__":
    validate_test_structure()
