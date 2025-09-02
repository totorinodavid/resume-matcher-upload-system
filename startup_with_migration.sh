#!/bin/bash
set -e

echo "🚨 STARTUP MIGRATION EXECUTION..."
echo "Current directory: $(pwd)"
echo "Python executable: $(which python)"
echo "Environment variables:"
env | grep -E "(DATABASE|ASYNC)" || echo "No database env vars found"

cd /app/apps/backend

echo "📋 Checking Alembic setup..."
if [ -f "alembic.ini" ]; then
    echo "✅ alembic.ini found"
    cat alembic.ini | head -20
else
    echo "❌ alembic.ini not found"
    ls -la
fi

echo "🔍 Running Alembic current..."
python -m alembic current || echo "Failed to get current revision"

echo "🚀 Running Alembic migration..."
python -m alembic upgrade head

echo "✅ Migration completed, starting application..."
exec python serve.py
