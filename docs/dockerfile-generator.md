# Dockerfile Generator

A specialized agent for generating production-ready Dockerfiles with multi-stage builds, layer caching optimization, and security best practices.

## Features

- **Multi-Stage Builds**: Optimized builder/runtime separation for smaller images
- **Layer Caching**: Intelligent ordering for faster rebuilds
- **Build Arguments**: Support for ARG instructions with proper handling
- **Secrets Handling**: BuildKit secret mounts for secure credential management
- **Health Checks**: Built-in HEALTHCHECK instruction configuration
- **Image Size Optimization**: Minimal final image with only runtime dependencies
- **Non-Root Users**: Secure user configuration to avoid running as root
- **Distroless Support**: Google's minimal distroless base images
- **Scratch Support**: Ultra-minimal images with only static binaries

## Usage

### Direct Agent Invocation

```yaml
agent: dockerfile-agent
input:
  build_type: multistage
  language: nodejs
  language_version: "20.x"
  build_command: npm run build
  start_command: npm start
  port: 3000
  healthcheck:
    cmd: "curl -f http://localhost:3000/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
    start_period: 40s
  environment_variables:
    NODE_ENV: production
  user: node
```

### Generated Output

The agent produces a production-ready multi-stage Dockerfile:

```dockerfile
# syntax=docker/dockerfile:1.4

# ============================================
# BUILDER STAGE
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files first for better layer caching
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# ============================================
# FINAL STAGE
# ============================================
FROM node:20-alpine AS final

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001

# Copy built artifacts from builder
COPY --from=builder --chown=nodeuser:nodejs /app/dist ./dist
COPY --from=builder --chown=nodeuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodeuser:nodejs /app/package.json ./

# Set environment variables
ENV NODE_ENV=production

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Switch to non-root user
USER nodeuser

# Start the application
CMD ["node", "dist/index.js"]
```

## Build Types

### Multi-Stage (Recommended)

Uses separate builder and runtime stages for optimal image size:

```yaml
input:
  build_type: multistage
  language: nodejs
  build_command: npm run build
  start_command: npm start
  port: 3000
```

**Benefits:**
- Smaller final image (no build tools)
- Better security (fewer dependencies)
- Faster deployment (smaller images)

### Single-Stage

All-in-one build and runtime environment:

```yaml
input:
  build_type: single-stage
  language: nodejs
  build_command: npm run build
  start_command: npm start
  port: 3000
```

**Use Cases:**
- Development and testing
- Quick prototyping
- When build tools are needed in production

### Distroless

Minimal runtime with Google's distroless images:

```yaml
input:
  build_type: distroless
  language: nodejs
  language_version: "20"
  builder_image: node:20-alpine
  final_image: gcr.io/distroless/nodejs20-debian11
  build_command: npm run build
  start_command: npm start
  port: 3000
```

**Benefits:**
- Minimal attack surface
- No shell or package manager
- Smaller than Alpine-based images

### Scratch

Empty base image for statically compiled binaries:

```yaml
input:
  build_type: scratch
  language: go
  build_command: go build -ldflags="-w -s" -o main ./cmd/server
  start_command: /main
  port: 8080
```

**Requirements:**
- Statically compiled binary
- No shell or utilities available
- All dependencies bundled

## Language Presets

| Language | Base Image | Default Port | Package Manager |
|----------|------------|--------------|-----------------|
| nodejs | node:20-alpine | 3000 | npm/yarn/pnpm |
| python | python:3.12-slim | 8000 | pip/poetry |
| go | golang:1.21-alpine | 8080 | go mod |
| rust | rust:1.70-alpine | 8080 | cargo |
| deno | deno:1.37-alpine | 8000 | deno |
| bun | oven/bun:1-alpine | 3000 | bun |
| static | nginx:alpine | 80 | npm |

## Health Check Configuration

### HTTP Health Check

```yaml
healthcheck:
  cmd: "curl -f http://localhost:3000/health || exit 1"
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 40s
```

### Alternative Health Check Commands

```yaml
# wget-based
healthcheck:
  cmd: "wget -qO- http://localhost:8080/health || exit 1"
  interval: 30s
  timeout: 5s
  retries: 3

# TCP port check
healthcheck:
  cmd: "nc -z localhost 5432 || exit 1"
  interval: 30s
  timeout: 5s
  retries: 3

# Custom script
healthcheck:
  cmd: "/usr/local/bin/healthcheck.sh"
  interval: 60s
  timeout: 10s
  retries: 5
```

## Environment Variables

### Static Variables

```yaml
environment_variables:
  NODE_ENV: production
  PORT: 3000
  LOG_LEVEL: info
  API_URL: https://api.example.com
```

### Runtime Secrets

```yaml
secrets:
  - DATABASE_URL
  - API_KEY
  - JWT_SECRET
```

The agent will use BuildKit secret mounts for build-time secrets:

```dockerfile
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    npm run build
```

## Build Arguments

### Version Information

```yaml
build_arguments:
  BUILD_DATE: "2024-01-15"
  SOURCE_COMMIT: "abc123"
  VERSION: "1.2.3"
```

Resulting Dockerfile:

```dockerfile
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG VERSION=latest

LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.source=$SOURCE_COMMIT \
      org.opencontainers.image.version=$VERSION
```

## Layer Caching Optimization

The agent automatically optimizes Dockerfile layer ordering:

1. **Dependencies first**: Copy package files before source code
2. **Combine commands**: Minimize layers with `&&`
3. **.dockerignore**: Exclude unnecessary files
4. **Smart ordering**: Least frequently changed items first

```dockerfile
# Layer 1: Dependencies (rarely change)
COPY package*.json ./
RUN npm ci

# Layer 2: Configuration (occasionally change)
COPY .env.production .env

# Layer 3: Source code (frequently changes)
COPY src/ ./src/

# Layer 4: Build output (changes with source)
RUN npm run build
```

## Non-Root User Configuration

```yaml
user: node
```

Generates:

```dockerfile
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodeuser -u 1001

# Set ownership of app directory
RUN mkdir /app && chown -R nodeuser:nodejs /app

USER nodeuser
```

## Custom Base Images

### Custom Builder Image

```yaml
builder_image: node:18-bullseye
```

### Custom Final Image

```yaml
final_image: gcr.io/distroless/nodejs18-debian11
```

### Full Custom Base

```yaml
base_image: ubuntu:22.04
```

## Examples

### Node.js Multi-Stage

```yaml
input:
  build_type: multistage
  language: nodejs
  language_version: "20.x"
  build_command: npm run build
  start_command: npm start
  port: 3000
  healthcheck:
    cmd: "curl -f http://localhost:3000/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
  environment_variables:
    NODE_ENV: production
  user: node
```

### Python Multi-Stage

```yaml
input:
  build_type: multistage
  language: python
  language_version: "3.12"
  build_command: pip install -r requirements.txt
  start_command: gunicorn app:app --bind 0.0.0.0:8000
  port: 8000
  healthcheck:
    cmd: "curl -f http://localhost:8000/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
  environment_variables:
    FLASK_ENV: production
  user: app
```

### Go Multi-Stage

```yaml
input:
  build_type: multistage
  language: go
  language_version: "1.21"
  build_command: go build -ldflags="-w -s" -o main ./cmd/server
  start_command: ./main
  port: 8080
  healthcheck:
    cmd: "wget -qO- http://localhost:8080/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
  user: app
```

### Rust Multi-Stage

```yaml
input:
  build_type: multistage
  language: rust
  language_version: "1.70"
  build_command: cargo build --release
  start_command: /app/server
  port: 8080
  environment_variables:
    RUST_LOG: info
  healthcheck:
    cmd: "curl -f http://localhost:8080/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
```

### Static Site

```yaml
input:
  build_type: multistage
  language: static
  build_command: npm run build
  output_directory: dist
  port: 80
  healthcheck:
    cmd: "wget -qO- http://localhost/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
  user: nginx
```

### Distroless

```yaml
input:
  build_type: distroless
  language: nodejs
  language_version: "20"
  build_command: npm run build
  start_command: npm start
  port: 3000
  builder_image: node:20-alpine
  final_image: gcr.io/distroless/nodejs20-debian11
  healthcheck:
    cmd: "curl -f http://localhost:3000/health || exit 1"
    interval: 30s
    timeout: 5s
    retries: 3
  environment_variables:
    NODE_ENV: production
  user: nonroot
```

## Validation

The agent validates generated Dockerfiles:

- Valid Dockerfile syntax
- Base images exist and are accessible
- Valid port range (1-65535)
- COPY paths are valid
- Health check commands are valid
- USER is created before use
- Layer ordering is optimized
- Security best practices are followed

## Best Practices

1. **Always use multi-stage builds** for production
2. **Use specific image tags**, never `latest`
3. **Run as non-root user** in production
4. **Configure health checks** for container orchestration
5. **Use BuildKit secrets** for sensitive build data
6. **Optimize layer caching** by ordering instructions
7. **Minimize image size** with minimal base images
8. **Use .dockerignore** to exclude unnecessary files
9. **Set appropriate labels** for image metadata
10. **Scan for vulnerabilities** (trivy, grype) regularly
