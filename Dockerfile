# Use Python 3.12 slim image for better performance
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/backend/requirements.txt /app/apps/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/apps/backend/requirements.txt

# Copy application code
COPY . /app/

# Copy startup script
COPY startup_with_migration.sh /app/startup_with_migration.sh
RUN chmod +x /app/startup_with_migration.sh

# Set Python path
ENV PYTHONPATH=/app/apps/backend

# Expose port
EXPOSE 8000

# Default command (will be overridden by render.yaml)
CMD ["/app/startup_with_migration.sh"]
