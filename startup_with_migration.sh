#!/bin/bash
set -e

echo "BULLETPROOF STARTUP WITH EMERGENCY MIGRATION"
echo "============================================="

# Run emergency migration check
./emergency_migration_check.sh fastapi run app/main.py --host 0.0.0.0 --port $PORT
