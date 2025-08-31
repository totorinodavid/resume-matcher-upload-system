FROM python:3.12-slim

# Prevent Python from writing .pyc files and ensure unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps/backend:/app/apps/backend/app

WORKDIR /app

# Install system dependencies that are commonly needed for Python packages
# (kept minimal; add more if runtime errors indicate missing libs)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Pre-copy pyproject.toml and uv.lock to leverage Docker layer caching
COPY apps/backend/pyproject.toml /app/apps/backend/pyproject.toml
COPY apps/backend/uv.lock /app/apps/backend/uv.lock

# Install Python dependencies using uv (global installation for Docker)
WORKDIR /app/apps/backend
RUN uv sync --frozen --no-dev --system

# Copy the full repo
WORKDIR /app
COPY . /app

# Default port (Railway injects PORT env and startCommand from railway.toml)
EXPOSE 8000
