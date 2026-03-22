# Multi-Stage Python Dockerfile Example

A production-optimized multi-stage Dockerfile for Python/FastAPI applications with Gunicorn, health checks, and security hardening.

## Input Specification

```yaml
# input.yaml
build_type: multistage
language: python
language_version: "3.12"
build_command: pip install -r requirements.txt
start_command: gunicorn app:app --bind 0.0.0.0:8000 --workers 4
port: 8000
healthcheck:
  cmd: "curl -f http://localhost:8000/health || exit 1"
  interval: 30s
  timeout: 5s
  retries: 3
environment_variables:
  FLASK_ENV: production
user: app
optimize_cache: true
minimize_layers: true
```

## Generated Dockerfile

```dockerfile
# Dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Production Runner
# ============================================
FROM python:3.12-slim AS runner

# Security: Create non-root user
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder --chown=app:app /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder --chown=app:app /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-"]
```

## Build Commands

```bash
# Build the image
docker build -t myapi:v1.0.0 .

# Build with BuildKit
DOCKER_BUILDKIT=1 docker build -t myapi:v1.0.0 .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  --name myapi \
  myapi:v1.0.0

# Run with secret mount
docker run -d \
  -p 8000:8000 \
  --secret id=api_key \
  --name myapi \
  myapi:v1.0.0

# Check logs
docker logs -f myapi

# Verify health status
docker inspect --format='{{.State.Health.Status}}' myapi
```

## Production Considerations

### Gunicorn Configuration
- 4 workers recommended for moderate traffic
- Worker type: sync (default) or gevent for async apps
- Pre-fork model for graceful restarts

### Security Hardening
- Non-root user (uid 1000)
- Read-only filesystem recommended
- No package manager cache
- Minimal runtime dependencies

### Health Check Implementation

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```
