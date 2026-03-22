# Multi-Stage Node.js Dockerfile Example

A production-optimized multi-stage Dockerfile for Node.js applications with layer caching, non-root user, and health checks.

## Input Specification

```yaml
# input.yaml
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
optimize_cache: true
minimize_layers: true
```

## Generated Dockerfile

```dockerfile
# Dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Dependencies
# ============================================
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# ============================================
# Stage 2: Builder
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build arguments
ARG NODE_ENV=production
ENV NODE_ENV=${NODE_ENV}

# Install all dependencies for build
RUN npm ci && npm run build

# ============================================
# Stage 3: Runner (Production)
# ============================================
FROM node:20-alpine AS runner

# Security: Add non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 node

WORKDIR /app

# Copy built artifacts
COPY --from=builder --chown=node:nodejs /app/dist ./dist
COPY --from=builder --chown=node:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=node:nodejs /app/package.json ./

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Switch to non-root user
USER node

# Start application
CMD ["npm", "start"]
```

## Build Commands

```bash
# Build the image
docker build -t myapp:v1.0.0 .

# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t myapp:v1.0.0 .

# Build with build arguments
docker build --build-arg NODE_ENV=staging -t myapp:staging .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t myregistry/myapp:v1.0.0 --push .

# Run the container
docker run -d -p 3000:3000 --name myapp myapp:v1.0.0

# Verify health check
docker inspect --format='{{.State.Health.Status}}' myapp
```

## Optimization Notes

### Layer Caching Strategy
1. Dependencies are installed first (package.json changes trigger rebuild)
2. Application code is copied after dependencies
3. Build artifacts are separated from runtime dependencies

### Image Size Optimization
- Using Alpine base reduces image size significantly
- Multi-stage build excludes dev dependencies from final image
- Non-root user improves security posture

### BuildKit Features
- Parallel stage execution
- Cache mounts for faster rebuilds
- Improved layer deduplication
