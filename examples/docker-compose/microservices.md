# Docker Compose Microservices Example

A production-ready Docker Compose configuration demonstrating a microservices architecture with isolated networks, service discovery, and orchestrated dependencies.

## Input Specification

```yaml
# input.yaml
compose_version: "3.8"
services:
  - name: gateway
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      - web
    depends_on:
      - api
      - worker
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
  - name: api
    build:
      context: ./services/api
      dockerfile: Dockerfile
    networks:
      - web
      - backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    healthcheck:
      test: "curl -f http://localhost:4000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  - name: worker
    build:
      context: ./services/worker
      dockerfile: Dockerfile
    networks:
      - backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
      QUEUE_URL: amqp://guest:guest@mq:5672
    depends_on:
      - db
      - redis
      - mq
    restart: unless-stopped
  - name: db
    image: postgres:15-alpine
    networks:
      - backend
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  - name: redis
    image: redis:7-alpine
    networks:
      - backend
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  - name: mq
    image: rabbitmq:3-management-alpine
    networks:
      - backend
    volumes:
      - mq_data:/var/lib/rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
networks:
  - name: web
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
  - name: backend
    driver: bridge
    ipam:
      config:
        - subnet: 172.29.0.0/16
volumes:
  - name: db_data
    driver: local
  - name: redis_data
    driver: local
  - name: mq_data
    driver: local
```

## Generated docker-compose.yml

```yaml
# docker-compose.yml
version: "3.8"

services:
  gateway:
    image: nginx:alpine
    container_name: gateway
    ports:
      - "80:80"
      - "443:443"
    networks:
      - web
    depends_on:
      - api
      - worker
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
    volumes:
      - ./services/gateway/nginx.conf:/etc/nginx/nginx.conf:ro

  api:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    container_name: api
    networks:
      - web
      - backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: "curl -f http://localhost:4000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"

  worker:
    build:
      context: ./services/worker
      dockerfile: Dockerfile
    container_name: worker
    networks:
      - backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
      QUEUE_URL: amqp://guest:guest@mq:5672
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      mq:
        condition: service_healthy
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "5"

  db:
    image: postgres:15-alpine
    container_name: db
    networks:
      - backend
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: redis
    networks:
      - backend
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "50m"
        max-file: "3"

  mq:
    image: rabbitmq:3-management-alpine
    container_name: mq
    networks:
      - backend
    volumes:
      - mq_data:/var/lib/rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped
    ports:
      - "15672:15672"
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"

networks:
  web:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
  backend:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.29.0.0/16

volumes:
  db_data:
    driver: local
  redis_data:
    driver: local
  mq_data:
    driver: local
```

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        web network                          │
│                    (172.28.0.0/16)                          │
│  ┌──────────┐                              ┌──────────┐    │
│  │ gateway  │ ──────────────────────────────│   api    │    │
│  │  (nginx) │                              │ (port    │    │
│  └──────────┘                              │  4000)   │    │
│     :80, :443                               └────┬─────┘    │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
                    ┌──────────────────────────────┼──────────┐
                    │        backend network      │          │
                    │       (172.29.0.0/16)       │          │
                    │                            ▼          │
                    │  ┌──────────┐     ┌──────────┐       │
                    │  │    db    │     │   redis  │       │
                    │  │(postgres)│     │          │       │
                    │  └──────────┘     └──────────┘       │
                    │        ▲              ▲              │
                    │        │              │              │
                    │        │              │              │
                    │  ┌─────┴──────┐     ┌─┴──────────┐   │
                    │  │   worker   │─────│     mq     │   │
                    │  │            │     │ (rabbitmq)│   │
                    │  └────────────┘     └───────────┘   │
                    └─────────────────────────────────────┘
```

## Common Commands

```bash
# Start entire stack
docker-compose up -d

# Build all services
docker-compose up -d --build

# View all services
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api worker

# Scale services
docker-compose up -d --scale worker=3

# Check network connectivity
docker-compose exec api ping worker
docker-compose exec worker ping db

# Health checks
docker-compose ps

# Access RabbitMQ management UI
open http://localhost:15672

# Stop and cleanup
docker-compose down -v

# Rebuild specific service
docker-compose up -d --build worker
```
