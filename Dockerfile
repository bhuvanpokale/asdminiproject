# PlacementPro Dockerfile
# Production-ready container image for Flask application

FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    DATABASE_FILE=/app/data/placementpro.db \
    SECRET_KEY=placementpro-production-secret-key

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for persistent SQLite data
RUN mkdir -p /app/data

# Copy project files
COPY app.py seed_data.py ./
COPY templates/ ./templates/
COPY static/ ./static/

# Run initial seed to prepare sample data in container
RUN python seed_data.py

# Expose application port
EXPOSE 5000

# Health check instruction for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start Flask application
CMD ["python", "app.py"]
