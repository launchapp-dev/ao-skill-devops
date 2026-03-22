# Docker Compose Web Application Stack Example

A production-ready Docker Compose configuration for a web application with API backend, PostgreSQL database, and Redis cache.

## Input Specification

```yaml
# input.yaml
compose_version: "3.8"
services:
  - name: api
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
      NODE_ENV: production
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    healthcheck:
      test: "curl -f http://localhost:3000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
  - name: db
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  - name: redis
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
networks:
  - name: backend
    driver: bridge
volumes:
  - name: db_data
    driver: local
  - name: redis_data
    driver: local
```

## Generated docker-compose.yml

```yaml
# docker-compose.yml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapp_api
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
      NODE_ENV: production
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: "curl -f http://localhost:3000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15-alpine
    container_name: myapp_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: myapp_redis
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - backend
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  backend:
    driver: bridge

volumes:
  db_data:
    driver: local
  redis_data:
    driver: local
```

## Common Commands

```bash
# Start all services
docker-compose up -d

# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f api
docker-compose logs -f

# Scale services
docker-compose up -d --scale api=3

# Check service health
docker-compose ps

# View resource usage
docker-compose top

# Stop and remove
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose up -d --build api
```

## Environment-Specific Configurations

### Development Override (docker-compose.override.yml)

```yaml
# docker-compose.override.yml
version: "3.8"

services:
  api:
    environment:
      NODE_ENV: development
      DEBUG: "true"
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "9229:9229"  # Debug port
    command: npm run dev:debug

  db:
    ports:
      - "5432:5432"  # Expose DB port for local access
```

### Production Override (docker-compose.prod.yml)

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  api:
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  db:
    restart: always
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    restart: always
    command: redis-server --appendonly yes
```

### Using Overrides

```bash
# Development (default override applied)
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
