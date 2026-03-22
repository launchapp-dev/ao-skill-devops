# Docker Compose Generator

A specialized agent for generating docker-compose.yml files for multi-service orchestration.

## Features

- **Multi-Service Orchestration**: Define and manage multiple services
- **Network Configuration**: Custom Docker networks with drivers and IPAM
- **Volume Management**: Named volumes and bind mounts
- **Environment Variables**: Object and array format support
- **Health Checks**: HTTP, TCP, and command-based health checks
- **Service Dependencies**: depends_on with conditionals
- **Restart Policies**: Configure container restart behavior
- **Logging Configuration**: Driver and options configuration
- **Secrets Management**: Docker secrets and configs support
- **Build Configuration**: Multi-stage and multi-service builds

## Usage

### Direct Agent Invocation

```yaml
agent: docker-compose-agent
input:
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
      depends_on:
        - db
        - redis
      healthcheck:
        test: "curl -f http://localhost:3000/health || exit 1"
        interval: 30s
        timeout: 10s
        retries: 3
      restart: unless-stopped
    - name: db
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: secret
        POSTGRES_DB: myapp
      volumes:
        - db_data:/var/lib/postgresql/data
    - name: redis
      image: redis:7-alpine
      volumes:
        - redis_data:/data
  networks:
    - name: backend
      driver: bridge
  volumes:
    - name: db_data
    - name: redis_data
```

### Generated Output

```yaml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
      NODE_ENV: production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: "curl -f http://localhost:3000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - backend

  db:
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
    networks:
      - backend

  redis:
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
      - backend

networks:
  backend:
    driver: bridge

volumes:
  db_data:
  redis_data:
```

## Compose Versions

| Version | Features |
|---------|----------|
| 3.8 | Recommended, supports all features |
| 3.9 | Latest, same feature set as 3.8 |
| 3.7 | Compatible with older Docker versions |
| 3.3 | Legacy, limited features |

## Service Configuration

### Image-Based Services

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
```

### Build-Based Services

```yaml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
      args:
        BUILD_VERSION: "1.0.0"
```

### Multi-Stage Build

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
```

## Port Mapping

### Single Port

```yaml
ports:
  - "8080:8080"
```

### Multiple Ports

```yaml
ports:
  - "8080:8080"
  - "8443:8443"
```

### UDP Ports

```yaml
ports:
  - "53:53/udp"
```

## Environment Variables

### Object Format (Recommended)

```yaml
environment:
  NODE_ENV: production
  DATABASE_URL: postgres://user:pass@host:5432/db
  LOG_LEVEL: info
```

### Array Format

```yaml
environment:
  - NODE_ENV=production
  - DATABASE_URL=postgres://user:pass@host:5432/db
```

### Environment File

```yaml
env_file:
  - .env.production
```

## Volume Mounts

### Named Volumes

```yaml
volumes:
  - db_data:/var/lib/postgresql/data
```

### Bind Mounts

```yaml
volumes:
  - ./data:/data:ro
  - ./logs:/var/log/myapp
```

### tmpfs Mounts

```yaml
volumes:
  - /tmp:/data:rw
```

## Network Configuration

### Bridge Network (Default)

```yaml
networks:
  - name: backend
    driver: bridge
```

### Custom Subnet

```yaml
networks:
  backend:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
```

### Host Network

```yaml
networks:
  host:
    driver: host
```

### External Network

```yaml
networks:
  existing:
    external: true
    name: my-existing-network
```

## Health Checks

### HTTP Health Check

```yaml
healthcheck:
  test: "curl -f http://localhost/health || exit 1"
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Docker HEALTHCHECK Format

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### PostgreSQL Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Redis Health Check

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### MySQL/MariaDB Health Check

```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## Service Dependencies

### Simple Dependencies

```yaml
depends_on:
  - db
  - redis
```

### Conditional Dependencies

```yaml
depends_on:
  db:
    condition: service_healthy
  redis:
    condition: service_started
```

| Condition | Description |
|-----------|-------------|
| `service_started` | Wait for container to start |
| `service_healthy` | Wait for health check to pass |

## Restart Policies

| Policy | Behavior |
|--------|----------|
| `no` | Never restart (default) |
| `always` | Always restart |
| `on-failure` | Restart on non-zero exit |
| `on-failure:3` | Restart up to 3 times on failure |
| `unless-stopped` | Restart unless stopped |

## Logging Configuration

### Basic Logging

```yaml
logging:
  driver: json-file
```

### With Options

```yaml
logging:
  driver: json-file
  options:
    max-size: "100m"
    max-file: "3"
```

### Syslog

```yaml
logging:
  driver: syslog
  options:
    syslog-address: "tcp://192.168.0.42:123"
```

## Secrets (Docker Swarm)

```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

## Configs (Docker Swarm)

```yaml
configs:
  nginx_config:
    file: ./config/nginx.conf
```

## Examples

### Basic Web Stack

```yaml
input:
  compose_version: "3.8"
  services:
    - name: web
      image: nginx:alpine
      ports:
        - "80:80"
      volumes:
        - "./html:/usr/share/nginx/html:ro"
      healthcheck:
        test: "curl -f http://localhost/ || exit 1"
        interval: 30s
        timeout: 5s
        retries: 3
      restart: unless-stopped
```

### Full Stack with Database

```yaml
input:
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
        REDIS_URL: redis://redis:6379
      depends_on:
        db:
          condition: service_healthy
        redis:
          condition: service_started
      healthcheck:
        test: "curl -f http://localhost:3000/health || exit 1"
        interval: 30s
        timeout: 10s
        retries: 3
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
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 10s
        timeout: 5s
        retries: 5
    - name: redis
      image: redis:7-alpine
      volumes:
        - redis_data:/data
      healthcheck:
        test: ["CMD", "redis-cli", "ping"]
        interval: 10s
        timeout: 5s
        retries: 5
  networks:
    - name: backend
      driver: bridge
  volumes:
    - name: db_data
    - name: redis_data
```

### Development Stack

```yaml
input:
  compose_version: "3.8"
  services:
    - name: app
      build:
        context: .
        dockerfile: Dockerfile.dev
      ports:
        - "3000:3000"
        - "9229:9229"
      environment:
        NODE_ENV: development
        DEBUG: "true"
      volumes:
        - ".:/app"
        - "/app/node_modules"
      tty: true
      stdin_open: true
      depends_on:
        - db
        - redis
        - mq
    - name: db
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: dev
        POSTGRES_PASSWORD: dev
        POSTGRES_DB: devdb
      ports:
        - "5432:5432"
      volumes:
        - pg_data:/var/lib/postgresql/data
    - name: redis
      image: redis:7-alpine
      ports:
        - "6379:6379"
      volumes:
        - redis_data:/data
    - name: mq
      image: rabbitmq:3-management
      ports:
        - "5672:5672"
        - "15672:15672"
      environment:
        RABBITMQ_DEFAULT_USER: guest
        RABBITMQ_DEFAULT_PASS: guest
      volumes:
        - rabbitmq_data:/var/lib/rabbitmq
  networks:
    - name: dev
      driver: bridge
  volumes:
    - name: pg_data
    - name: redis_data
    - name: rabbitmq_data
```

### Production with Secrets

```yaml
input:
  compose_version: "3.8"
  services:
    - name: api
      image: myregistry/myapp:v1.0.0
      ports:
        - "8080:8080"
      secrets:
        - db_password
        - api_key
      environment:
        NODE_ENV: production
        DATABASE_HOST: db
      depends_on:
        db:
          condition: service_healthy
      healthcheck:
        test: "curl -f http://localhost:8080/health || exit 1"
        interval: 30s
        timeout: 10s
        retries: 3
        start_period: 30s
      restart: unless-stopped
      logging:
        driver: json-file
        options:
          max-size: "100m"
          max-file: "3"
    - name: db
      image: postgres:15-alpine
      volumes:
        - db_data:/var/lib/postgresql/data
      secrets:
        - db_password
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 10s
        timeout: 5s
        retries: 5
  networks:
    - name: production
      driver: bridge
  volumes:
    - name: db_data
  secrets:
    - name: db_password
      file: ./secrets/db_password.txt
    - name: api_key
      file: ./secrets/api_key.txt
```

### Custom Networks

```yaml
input:
  compose_version: "3.8"
  services:
    - name: frontend
      image: nginx:alpine
      ports:
        - "80:80"
        - "443:443"
      networks:
        - web
      depends_on:
        - api
    - name: api
      build:
        context: ./api
        dockerfile: Dockerfile
      networks:
        - web
        - backend
      environment:
        DATABASE_URL: postgresql://user:pass@db:5432/mydb
      depends_on:
        - db
    - name: worker
      build:
        context: ./worker
        dockerfile: Dockerfile
      networks:
        - backend
      depends_on:
        - db
        - redis
    - name: db
      image: postgres:15-alpine
      networks:
        - backend
      volumes:
        - db_data:/var/lib/postgresql/data
    - name: redis
      image: redis:7-alpine
      networks:
        - backend
      volumes:
        - redis_data:/data
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
    - name: redis_data
```

## Validation

The agent validates generated configurations:

- YAML syntax correctness
- Valid compose version
- Unique service names
- Valid port numbers (1-65535)
- Valid volume paths
- Unique network names
- Valid health check commands
- Valid environment variable names

## Best Practices

1. **Use named volumes** for persistent data
2. **Configure health checks** for critical services
3. **Set appropriate restart policies** (use `unless-stopped` for services)
4. **Pin image versions** (avoid `latest` tag)
5. **Use secrets** for sensitive data in production
6. **Configure logging** for production services
7. **Use conditional depends_on** for service startup order
8. **Separate networks** for security (web vs. backend)
9. **Set resource limits** for production workloads
10. **Use .dockerignore** to exclude unnecessary files

## Related

- [Dockerfile Generator](dockerfile-generator.md) - Dockerfile generation
- [Integration Testing](integration-testing.md) - Test infrastructure
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose file reference](https://docs.docker.com/compose/compose-file/)
