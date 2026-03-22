# ao-skill-devops

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Maintenance](https://img.shields.io/badge/Maintenance-active-brightgreen.svg)](#maintenance)
[![AO Pack](https://img.shields.io/badge/AO-Pack-blue.svg)](https://github.com/launchapp-dev/ao-skills)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](pack.toml)

> Generate GitHub Actions, Dockerfiles, Kubernetes manifests, Railway configs, Vercel configs, and deployment configurations automatically using AI agents.

## Overview

`ao-skill-devops` is an AO (Agent Orchestrator) skill pack that provides specialized agents for generating DevOps configuration files. It includes generators for:

- **Kubernetes Manifests**: Deployments, Services, Ingress, ConfigMaps, Secrets, PVCs, Helm charts, Kustomize overlays
- **GitHub Actions**: CI/CD pipelines for Node.js, Python, and Go with linting, testing, caching, and Docker support
- **Dockerfiles**: Multi-stage builds with layer caching, health checks, and security best practices
- **Docker Compose**: Multi-service orchestration with networks, volumes, and health checks
- **Railway Configs**: Docker and Nixpacks deployments with health checks and autoscaling
- **Vercel Configs**: Static sites, serverless functions, edge functions, and monorepos
- **Python CI**: GitHub Actions workflows with pytest and coverage threshold enforcement
- **Agent Base Framework**: Foundation classes for DevOps generator agents

## Status

| Generator | Status | Documentation |
|-----------|--------|---------------|
| Kubernetes Manifest Generator | Stable | [docs/k8s-manifest-generator.md](docs/k8s-manifest-generator.md) |
| GitHub Actions Generator | Stable | [docs/github-actions-generator.md](docs/github-actions-generator.md) |
| Dockerfile Generator | Stable | [docs/dockerfile-generator.md](docs/dockerfile-generator.md) |
| Docker Compose Generator | Stable | [docs/docker-compose-generator.md](docs/docker-compose-generator.md) |
| Railway Config Generator | Stable | [docs/railway-config-generator.md](docs/railway-config-generator.md) |
| Railway Config Tester | Stable | [docs/railway-config-tester.md](docs/railway-config-tester.md) |
| Vercel Config Generator | Stable | [docs/vercel-config-generator.md](docs/vercel-config-generator.md) |
| Python CI Generator | Stable | [docs/python-ci-generator.md](docs/python-ci-generator.md) |
| Agent Base Framework | Stable | [docs/agent-base-framework.md](docs/agent-base-framework.md) |
| Integration Tester | Stable | [docs/integration-testing.md](docs/integration-testing.md) |

## Installation

### Using AO CLI

Install the skill pack via AO CLI:

```bash
# Install all generators
ao pack install github:launchapp-dev/ao-skill-devops

# Install specific generators
ao pack install github:launchapp-dev/ao-skill-devops --skills k8s-manifest-generator,dockerfile-generator
```

### Using pack.toml

Add to your project's `pack.toml`:

```toml
[skills]
exports = [
  # Choose the generators you need
  "ao.devops/k8s-manifest-generator",
  "ao.devops/github-actions-generator",
  "ao.devops/dockerfile-generator",
  "ao.devops/docker-compose-generator",
  "ao.devops/railway-config-generator",
  "ao.devops/vercel-config-generator",
  "ao.devops/python-ci-generator",
  "ao.devops/agent-base-framework",
  "ao.devops/integration-tester",
]
```

## Quick Start

### 1. Generate a Dockerfile

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
  environment_variables:
    NODE_ENV: production
  user: node
```

### 2. Generate Kubernetes Manifests

```yaml
agent: k8s-manifest-agent
input:
  manifest_type: deployment
  name: my-application
  namespace: production
  replicas: 3
  image: myregistry/myapp:v1.2.3
  ports:
    - name: http
      containerPort: 8080
      servicePort: 80
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### 3. Generate GitHub Actions CI

```yaml
agent: github-actions-agent
input:
  environment: nodejs
  workflow_type: ci
  name: Node.js CI
  language_version: "20.x"
  steps:
    - lint
    - test
    - build
  cache: true
  matrix:
    os: [ubuntu-latest, macos-latest]
    node-version: ["18.x", "20.x"]
```

### 4. Generate Docker Compose

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

### 5. Generate Railway Config

```yaml
agent: railway-config-agent
input:
  deployment_type: docker
  dockerfile_path: Dockerfile
  port: 8080
  num_replicas: 2
  healthcheck_path: /health
  environment_variables:
    NODE_ENV: production
    PORT: 8080
  secret_variables:
    - DATABASE_URL
    - API_KEY
  memory_limit: 512
  cpu: 1
```

### 6. Generate Vercel Config

```yaml
agent: vercel-config-agent
input:
  deployment_type: serverless
  framework: nextjs
  regions:
    - iad1
    - sfo1
  build_command: npm run build
  output_directory: .next
  environment_variables:
    NODE_ENV: production
  secret_environment_variables:
    - DATABASE_URL
    - API_KEY
  functions:
    api:
      runtime: nodejs18.x
      memory: 1024
      maxDuration: 10
```

### 7. Generate Python CI

```yaml
agent: python-ci-agent
input:
  environment: python
  name: Python CI
  version: "3.11"
  package_manager: poetry
  coverage_threshold: 80
  fail_under: 80
  lint: true
  linter: ruff
  cache: true
```

## All Generators

### Core Generators

| Generator | ID | Description |
|-----------|-----|-------------|
| Kubernetes Manifest | `ao.devops/k8s-manifest-generator` | K8s Deployments, Services, Ingress, ConfigMaps, Secrets, PVCs, Helm, Kustomize |
| GitHub Actions | `ao.devops/github-actions-generator` | CI/CD for Node.js, Python, Go with lint/test/build/caching |
| Dockerfile | `ao.devops/dockerfile-generator` | Multi-stage Dockerfiles with layer caching and health checks |
| Docker Compose | `ao.devops/docker-compose-generator` | Multi-service orchestration |

### Platform Deployments

| Generator | ID | Description |
|-----------|-----|-------------|
| Railway Config | `ao.devops/railway-config-generator` | Railway.toml for Docker, Nixpacks, monorepos |
| Vercel Config | `ao.devops/vercel-config-generator` | vercel.json for static, serverless, edge, monorepos |

### CI/CD Specific

| Generator | ID | Description |
|-----------|-----|-------------|
| Python CI | `ao.devops/python-ci-generator` | Python GitHub Actions with pytest and coverage |
| Python CI Tests | `ao.devops/railway-config-tester` | Unit tests for Railway configs |
| Vercel Config Tests | `ao.devops/vercel-config-generator-tests` | Unit tests for Vercel configs |

### Infrastructure

| Generator | ID | Description |
|-----------|-----|-------------|
| Agent Base Framework | `ao.devops/agent-base-framework` | Foundation classes for DevOps agents |
| Integration Tester | `ao.devops/integration-tester` | E2E testing for generated configs |

## Workflows

This skill pack provides the following workflows:

| Workflow | Description |
|----------|-------------|
| `ao.devops/standard` | Plan → Implement → Push → PR → Review |
| `ao.devops/quick-fix` | Implement → Push → PR |
| `ao.devops/k8s-manifest` | Generate K8s manifests → Push → PR → Review |
| `ao.devops/standard-with-tests` | Plan → Implement → Integration Test → Push → PR |
| `ao.devops/github-actions` | Generate GitHub Actions workflows |
| `ao.devops/python-ci` | Generate Python CI with pytest and coverage |
| `ao.devops/vercel-config` | Generate Vercel deployment configs |
| `ao.devops/vercel-config-with-tests` | Generate Vercel configs with unit tests |
| `ao.devops/railway-config` | Generate Railway deployment configs |
| `ao.devops/dockerfile` | Generate production Dockerfiles |
| `ao.devops/docker-compose` | Generate docker-compose files |
| `ao.devops/base-framework` | Generate agent base framework |

### Running Workflows

```bash
# Run the standard workflow
ao workflow run --workflow ao.devops/standard --task-id TASK-001

# Run K8s manifest generation
ao workflow run --workflow ao.devops/k8s-manifest --task-id TASK-002

# Run with custom parameters
ao workflow run --workflow ao.devops/dockerfile --task-id TASK-003 \
  --input '{"build_type": "multistage", "language": "nodejs"}'
```

## Examples Gallery

Comprehensive examples with realistic use cases are available in the [`examples/`](examples/) directory:

### Language-Specific Examples

| Category | Examples |
|----------|----------|
| **Node.js** | [Express.js REST API](examples/nodejs/express-api.md), [Bull Queue Workers](examples/nodejs/worker.md) |
| **Python** | [FastAPI Async Service](examples/python/fastapi-service.md), [Django with Celery](examples/python/django-app.md) |
| **Go** | [HTTP Server](examples/go/http-server.md), [gRPC Microservice](examples/go/grpc-service.md) |
| **Multi-Service** | [Web App Stack](examples/multi-service/web-app.md), [E-commerce Platform](examples/multi-service/ecommerce.md) |

### Example Contents

Each example includes:
- **Input specification** (YAML) for the generator
- **Generated configurations** (Dockerfile, K8s manifests, GitHub Actions, etc.)
- **Best practices** for production deployments
- **Additional configurations** (HPA, Ingress, health checks)

## Documentation

### Generator Documentation

| Document | Description |
|----------|-------------|
| [Kubernetes Manifest Generator](docs/k8s-manifest-generator.md) | K8s manifest generation with examples |
| [GitHub Actions Generator](docs/github-actions-generator.md) | CI/CD pipeline generation |
| [Dockerfile Generator](docs/dockerfile-generator.md) | Multi-stage Dockerfile generation |
| [Docker Compose Generator](docs/docker-compose-generator.md) | Multi-service orchestration |
| [Railway Config Generator](docs/railway-config-generator.md) | Railway deployment configs |
| [Railway Config Tester](docs/railway-config-tester.md) | Unit tests for Railway configs |
| [Vercel Config Generator](docs/vercel-config-generator.md) | Vercel deployment configs |
| [Python CI Generator](docs/python-ci-generator.md) | Python CI workflows |
| [Agent Base Framework](docs/agent-base-framework.md) | Framework foundations |
| [Integration Testing](docs/integration-testing.md) | E2E testing infrastructure |

### API Documentation

- [API Reference](docs/api.md) - Programmatic usage and SDK

### Contributing

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow and guidelines
- [VISION.md](VISION.md) - Product vision and roadmap

## Best Practices

### Kubernetes

1. **Always specify namespace**: Don't rely on the default namespace
2. **Set resource limits**: Prevent runaway resource consumption
3. **Configure health probes**: Ensure proper pod lifecycle management
4. **Use secrets for sensitive data**: Never hardcode credentials
5. **Use labels consistently**: Enable proper selector matching

### Docker

1. **Use multi-stage builds** for production
2. **Run as non-root user** in production
3. **Configure health checks** for container orchestration
4. **Use specific image tags**, never `latest`
5. **Optimize layer caching** by ordering instructions

### GitHub Actions

1. **Always specify versions**: Pin language versions for reproducibility
2. **Use caching**: Speed up builds with dependency caching
3. **Add timeouts**: Prevent runaway jobs with sensible timeouts
4. **Use matrix builds**: Test across multiple versions/platforms
5. **Set artifact retention**: Configure appropriate retention periods

### Railway

1. **Configure health checks** for production services
2. **Use `${{ secrets.VAR }}`** for sensitive configuration
3. **Set appropriate resource limits** based on workload
4. **Use `$PORT`** for dynamic port binding
5. **Set healthcheck retries** for slow-starting services

### Vercel

1. **Specify explicit regions** for latency optimization
2. **Use `${{ secrets.VAR }}`** for sensitive values
3. **Configure proper cache headers** for static assets
4. **Set appropriate `maxDuration`** for long-running functions
5. **Configure CORS headers** for API routes

## Maintenance

This project is actively maintained by the [launchapp-dev](https://github.com/launchapp-dev) team.

- **Version**: 0.1.0
- **AO Core Compatibility**: >=0.2.0
- **Workflow Schema**: v2

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [AO CLI](https://github.com/launchapp-dev/ao)
- [AO Skills](https://github.com/launchapp-dev/ao-skills)
- [AO Docs](https://github.com/launchapp-dev/ao-docs)
- [GitHub Repository](https://github.com/launchapp-dev/ao-skill-devops)
