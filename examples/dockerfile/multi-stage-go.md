# Multi-Stage Go Dockerfile Example

A production-optimized multi-stage Dockerfile for Go applications with static binary output and minimal attack surface.

## Input Specification

```yaml
# input.yaml
build_type: multistage
language: go
language_version: "1.21"
build_command: go build -o main ./cmd/server
start_command: ./main
port: 8080
healthcheck:
  cmd: "wget -qO- http://localhost:8080/health || exit 1"
  interval: 30s
  timeout: 5s
  retries: 3
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
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /app

# Copy go mod files first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build arguments
ARG VERSION=dev
ARG COMMIT_SHA=unknown
ARG BUILD_DATE=unknown

# Build the application
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    VERSION=${VERSION} \
    COMMIT_SHA=${COMMIT_SHA} \
    BUILD_DATE=${BUILD_DATE}

RUN go build -ldflags="\
    -s -w \
    -X main.Version=${VERSION} \
    -X main.CommitSHA=${COMMIT_SHA} \
    -X main.BuildDate=${BUILD_DATE}" \
    -o main ./cmd/server

# ============================================
# Stage 2: Scratch Runner (Minimal)
# ============================================
FROM scratch AS runner

# Security: No root user in scratch, use built-in nobody
# Copy CA certificates for HTTPS calls
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy timezone data
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# Copy the binary
COPY --from=builder /app/main /main

# Expose port
EXPOSE 8080

# Health check using wget (install in runtime stage)
COPY --from=builder /bin/wget /bin/wget
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:8080/health || exit 1

# Run as non-root
USER 65532:65532

ENTRYPOINT ["/main"]
```

## Alternative: Distroless Base Image

For containers that need shell access for debugging:

```dockerfile
# Dockerfile with distroless
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN go build -ldflags="-s -w" -o main ./cmd/server

# Use distroless as base
FROM gcr.io/distroless/static:nonroot AS runner

COPY --from=builder /app/main /main

USER nonroot:nonroot
ENTRYPOINT ["/main"]
```

## Build Commands

```bash
# Build the image
docker build -t myservice:v1.0.0 .

# Build with build arguments
docker build \
  --build-arg VERSION=1.0.0 \
  --build-arg COMMIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -t myservice:v1.0.0 .

# Multi-stage build verification
docker build --target builder -t myservice:debug .

# Run the container
docker run -d -p 8080:8080 --name myservice myservice:v1.0.0

# Check logs
docker logs myservice

# Verify health
docker inspect --format='{{.State.Health.Status}}' myservice
```

## Build Optimization Tips

### Go Module Caching
- Copy go.mod/go.sum first
- Run `go mod download` before copying code
- Cache hits on dependency layer

### Binary Size Reduction
```bash
# Strip debug symbols
go build -ldflags="-s -w"

# Use UPX compression (optional)
upx -9 main
```

### Multi-Platform Builds
```bash
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry/myservice:v1.0.0 \
  --push .
```

## Health Check Implementation

```go
package main

import (
    "net/http"
    "os"
)

func main() {
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte(`{"status":"ok"}`))
    })
    
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }
    
    http.ListenAndServe(":"+port, nil)
}
```
