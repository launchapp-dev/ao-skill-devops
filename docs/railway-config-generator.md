# Railway Config Generator

A specialized agent for generating Railway deployment configurations.

## Features

- **Docker Deployments**: Explicit Dockerfile-based deployments
- **Nixpacks Builds**: Auto-detection for Node.js, Python, Go, Rust, and more
- **Monorepo Support**: Multi-service Railway projects
- **Health Checks**: HTTP, TCP, and command-based health checks
- **Auto-scaling**: Configurable replica counts and resource limits
- **Environment Variables**: Static and secret-based configuration
- **Volume Mounts**: Persistent storage configuration
- **Service Bindings**: Database and managed service integration

## Usage

### Direct Agent Invocation

```yaml
agent: railway-config-agent
input:
  deployment_type: docker
  dockerfile_path: Dockerfile
  docker_context: .
  port: 8080
  num_replicas: 2
  healthcheck_path: /health
  healthcheck_interval: 30
  healthcheck_timeout: 5
  healthcheck_retries: 3
  environment_variables:
    NODE_ENV: production
    PORT: 8080
  secret_variables:
    - DATABASE_URL
    - API_KEY
  memory_limit: 512
  cpu: 1
```

### Generated Output

The agent produces valid `railway.toml` that can be deployed directly:

```toml
[build]
  builder = "dockerfile"
  dockerfile_path = "Dockerfile"
  context = "."

[deploy]
  num_replicas = 2
  restart_policy_type = "always"
  restart_policy_retries = 10

[healthcheck]
  path = "/health"
  interval = 30
  timeout = 5
  retries = 3

[environment]
  NODE_ENV = "production"
  PORT = "8080"
  DATABASE_URL = "${{ secrets.DATABASE_URL }}"
  API_KEY = "${{ secrets.API_KEY }}"

[resources]
  memory = "512"
  cpu = "1"
```

## Deployment Types

### Docker Deployment

```yaml
input:
  deployment_type: docker
  dockerfile_path: ./Dockerfile
  docker_context: .
  port: 8080
  environment_variables:
    NODE_ENV: production
```

### Nixpacks Node.js

```yaml
input:
  deployment_type: nixpacks
  language: nodejs
  build_command: npm run build
  start_command: npm start
  port: 3000
  healthcheck_path: /health
  environment_variables:
    NODE_ENV: production
```

### Nixpacks Python

```yaml
input:
  deployment_type: nixpacks
  language: python
  build_command: pip install -r requirements.txt
  start_command: gunicorn app:app
  port: 8000
  healthcheck_path: /health
  healthcheck_retries: 5
```

### Monorepo Multi-Service

```yaml
input:
  deployment_type: monorepo
  services:
    - name: api
      path: ./services/api
      deployment_type: docker
      dockerfile_path: ./services/api/Dockerfile
      port: 4000
      healthcheck_path: /health
    - name: worker
      path: ./services/worker
      deployment_type: nixpacks
      language: nodejs
      port: 4001
    - name: web
      path: ./apps/web
      deployment_type: nixpacks
      language: nodejs
      port: 3000
```

## Language Presets

| Language | Auto-Detection | Build Tools |
|----------|----------------|-------------|
| nodejs | package.json | npm, yarn, pnpm |
| python | requirements.txt | pip, poetry |
| go | go.mod | go build |
| rust | Cargo.toml | cargo build |
| deno | deno.json | deno task |
| bun | bun.lockb | bun |
| java | pom.xml, build.gradle | mvn, gradle |
| ruby | Gemfile | bundle |
| php | composer.json | composer |

## Health Check Configuration

### HTTP Health Check

```yaml
healthcheck_path: /health
healthcheck_interval: 30
healthcheck_timeout: 5
healthcheck_retries: 3
```

### TCP Health Check

```yaml
healthcheck_port: 5432
healthcheck_interval: 15
```

### Command Health Check

```yaml
healthcheck_command: /bin/check-health
healthcheck_interval: 60
```

## Environment Variables

### Static Variables

```yaml
environment_variables:
  NODE_ENV: production
  PORT: 8080
  LOG_LEVEL: info
```

### Secret Variables

```yaml
secret_variables:
  - DATABASE_URL
  - API_KEY
  - STRIPE_SECRET
  - JWT_SECRET
```

### Platform Variables

Railway automatically provides these variables:
- `$PORT` - Dynamic port assignment
- `$RAILWAY_STATIC_URL` - Public URL for static mounts
- `$RAILWAY_PRIVATE_DOMAIN` - Internal service domain

## Resource Configuration

### Memory Limit

```yaml
memory_limit: 512  # MB
```

### CPU Allocation

```yaml
cpu: 1  # Number of vCPUs
```

### Replica Scaling

```yaml
num_replicas: 3
```

## Docker Configuration

### Basic Docker Build

```toml
[build]
  builder = "dockerfile"
  dockerfile_path = "Dockerfile"
```

### Multi-Stage Build

```toml
[build]
  builder = "dockerfile"
  dockerfile_path = "Dockerfile.prod"
  docker_context = "./"
```

### Build Arguments

Set `ARG` values in your Dockerfile and Railway will use them automatically.

## Nixpacks Configuration

### Auto-Detection

```toml
[build]
  builder = "nixpacks"
```

### Custom Build/Start Commands

```toml
[build]
  builder = "nixpacks"
  build_command = "npm run build"
  start_command = "npm start"
```

## Monorepo Services

Each service can have its own configuration:

```yaml
services:
  - name: api
    path: ./services/api
    deployment_type: docker
    dockerfile_path: ./services/api/Dockerfile
    port: 4000
  - name: web
    path: ./apps/web
    deployment_type: nixpacks
    language: nodejs
    port: 3000
```

## Validation

The agent validates generated configurations:

- TOML syntax correctness
- Valid builder type (dockerfile, nixpacks, buildpack)
- Valid port range (1-65535)
- Valid healthcheck path format
- Proper secret variable references
- Resource values within Railway limits

## Best Practices

1. Always configure health checks for production services
2. Use `${{ secrets.VAR }}` for sensitive configuration
3. Set appropriate resource limits based on workload
4. Use `$PORT` for dynamic port binding
5. Configure healthcheck retries for slow-starting services
6. Use Nixpacks for quick prototyping and simple apps
7. Use Docker for precise control and complex builds
8. Set multiple replicas for high availability
9. Use healthcheck intervals appropriate to your service
