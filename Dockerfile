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
       build-essential \
       curl \
    && rm -rf /var/lib/apt/lists/*

# EMERGENCY FIX: Use traditional pip instead of uv for reliable Stripe installation
# Copy requirements.txt for pip installation
COPY apps/backend/requirements.txt /app/apps/backend/requirements.txt

# Install Python dependencies using pip (more reliable for Stripe)
WORKDIR /app/apps/backend
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verify Stripe installation
RUN python -c "import stripe; print(f'✅ Stripe {stripe.__version__} installed successfully')"

# Copy the full repo
WORKDIR /app
COPY . /app

# Default port (Railway injects PORT env and startCommand from railway.toml)
EXPOSE 8000
