# Railway Config Tester

Unit testing infrastructure for the Railway config generator skill pack. Validates TOML syntax, Docker deployments, Nixpacks builds, monorepo services, health checks, and environment variables generation.

## Overview

The Railway Config Tester provides comprehensive unit testing for generated `railway.toml` configurations. It ensures that configurations are syntactically correct, follow Railway best practices, and produce valid deployments.

## Features

- **TOML Syntax Validation**: Validates TOML structure and syntax correctness
- **Docker Deployment Tests**: Tests Dockerfile-based Railway deployments
- **Nixpacks Build Tests**: Tests Nixpacks-based auto-build configurations
- **Monorepo Service Tests**: Tests multi-service Railway project configurations
- **Health Check Tests**: Tests HTTP, TCP, and command-based health checks
- **Environment Variable Tests**: Tests static and secret environment variables

## Usage

### Direct Agent Invocation

```yaml
agent: integration-tester-agent
input:
  test_type: docker_deployments
  test_scenario: docker_deployment
  validation_level: strict
```

### Generated Test Scenarios

The tester includes pre-defined test scenarios for common Railway configurations:

#### Docker Deployment Test

```yaml
input:
  test_type: docker_deployments
  test_scenario: docker_deployment
  validation_level: strict
```

Expected configuration structure:
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

[resources]
  memory = "512"
  cpu = "1"
```

#### Nixpacks Node.js Test

```yaml
input:
  test_type: nixpacks_builds
  test_scenario: nixpacks_nodejs
  validation_level: strict
```

Expected configuration structure:
```toml
[build]
  builder = "nixpacks"
  build_command = "npm run build"
  start_command = "npm start"

[deploy]
  num_replicas = 1

[healthcheck]
  path = "/health"

[environment]
  NODE_ENV = "production"
```

#### Nixpacks Python Test

```yaml
input:
  test_type: nixpacks_builds
  test_scenario: nixpacks_python
  validation_level: strict
```

Expected configuration structure:
```toml
[build]
  builder = "nixpacks"
  build_command = "pip install -r requirements.txt"
  start_command = "gunicorn app:app"

[healthcheck]
  path = "/health"
  retries = 5

[environment]
  FLASK_ENV = "production"
```

#### Monorepo Multi-Service Test

```yaml
input:
  test_type: monorepo_services
  test_scenario: monorepo_multi_service
  validation_level: strict
```

Expected configuration structure:
```toml
[[services]]
  name = "api"
  path = "./services/api"

[[services]]
  name = "worker"
  path = "./services/worker"

[[services]]
  name = "web"
  path = "./apps/web"
```

#### Health Check HTTP Test

```yaml
input:
  test_type: health_checks
  test_scenario: healthcheck_http
  validation_level: strict
```

Expected configuration structure:
```toml
[healthcheck]
  path = "/health"
  interval = 30
  timeout = 5
  retries = 3
```

#### Health Check TCP Test

```yaml
input:
  test_type: health_checks
  test_scenario: healthcheck_tcp
  validation_level: strict
```

Expected configuration structure:
```toml
[healthcheck]
  port = 5432
  interval = 15
```

#### Health Check Command Test

```yaml
input:
  test_type: health_checks
  test_scenario: healthcheck_command
  validation_level: strict
```

Expected configuration structure:
```toml
[healthcheck]
  command = "/bin/check-health"
  interval = 60
```

#### Environment Variables Test (Static)

```yaml
input:
  test_type: environment_variables
  test_scenario: env_static
  validation_level: strict
```

Expected configuration structure:
```toml
[environment]
  NODE_ENV = "production"
  PORT = "3000"
  LOG_LEVEL = "info"
  API_URL = "https://api.example.com"
```

#### Environment Variables Test (with Secrets)

```yaml
input:
  test_type: environment_variables
  test_scenario: env_with_secrets
  validation_level: strict
```

Expected configuration structure:
```toml
[environment]
  NODE_ENV = "production"
  DATABASE_URL = "${{ secrets.DATABASE_URL }}"
  API_KEY = "${{ secrets.API_KEY }}"
  STRIPE_SECRET = "${{ secrets.STRIPE_SECRET }}"
  JWT_SECRET = "${{ secrets.JWT_SECRET }}"
```

## Test Categories

### 1. Docker Deployments

Tests Docker-based Railway deployments including:
- Basic Docker build configuration
- Multi-stage Dockerfile support
- Docker context override
- Dockerfile path validation
- Docker with health checks
- Docker with resource limits

### 2. Nixpacks Builds

Tests Nixpacks-based Railway deployments including:
- Node.js detection and build
- Python detection and build
- Go detection and build
- Rust detection and build
- Custom build command override
- Language auto-detection

### 3. Monorepo Services

Tests monorepo/multi-service Railway deployments including:
- Multi-service Docker configurations
- Multi-service Nixpacks configurations
- Mixed build types (Docker + Nixpacks)
- Service dependency ordering
- Monorepo path validation

### 4. Health Checks

Tests health check configurations including:
- HTTP endpoint health checks
- TCP port health checks
- Command-based health checks
- Health check timing parameters
- Health check retry configuration
- Health check disabling

### 5. Environment Variables

Tests environment variable configurations including:
- Static environment variables
- Secret references (`${{ secrets.VAR }}`)
- Mixed static and secret variables
- Platform-provided variables (`$PORT`, `$RAILWAY_*`)
- Environment variable name validation

## Validation Rules

### TOML Syntax Validation

| Rule | Description |
|------|-------------|
| UTF-8 encoding | TOML must be valid UTF-8 |
| Table definitions | All tables must be properly defined |
| String quoting | String values must be properly quoted |
| Number validation | Numbers must be valid integers or floats |
| Array consistency | Arrays must have consistent types |

### Builder Type Validation

Valid Railway builder types:
- `docker` - Dockerfile-based deployment
- `nixpacks` - Auto-detected build
- `buildpack` - Heroku-style buildpacks

### Port Range Validation

Valid port range: **1-65535**

### Resource Limits

| Resource | Minimum | Maximum |
|----------|---------|---------|
| Memory (MB) | 64 | 65536 |
| CPU (vCPU) | 0.1 | 16 |

## Validation Levels

| Level | Description |
|-------|-------------|
| `strict` | Enforce all schema requirements, fail on warnings |
| `moderate` | Enforce schema, allow minor best practice issues |
| `lenient` | Only check required fields and basic syntax |

## Output Format

Tests return structured results:

```json
{
  "passed": true,
  "duration_ms": 1523,
  "test_type": "docker_deployments",
  "target_file": "./output/railway.toml",
  "errors": [],
  "warnings": [
    {
      "message": "Consider adding health checks for production services",
      "line": 15,
      "severity": "warning",
      "rule": "healthcheck-recommended"
    }
  ],
  "validation_details": {
    "toml_valid": true,
    "builder_valid": true,
    "port_valid": true,
    "healthcheck_valid": true,
    "env_vars_valid": true,
    "resources_valid": true
  },
  "recommendations": [
    "Add health check endpoint for better reliability",
    "Consider setting explicit resource limits"
  ]
}
```

## Best Practices

1. **Always validate TOML syntax** before deploying
2. **Use `strict` validation level** for production configurations
3. **Test all deployment scenarios** (Docker, Nixpacks, monorepo)
4. **Verify health check paths** are accessible
5. **Use secret references** for sensitive data
6. **Set appropriate resource limits** based on workload
7. **Review recommendations** even when tests pass

## Integration with Workflows

The Railway Config Tester integrates with the `ao.devops/railway-config` workflow:

```yaml
workflows:
  - id: ao.devops/railway-config
    name: "Railway Config Generator"
    description: "Generate Railway deployment configurations (railway.toml) for Docker containers, Nixpacks builds, and monorepo services"
    phases:
      - railway-config-generate
      - railway-config-test  # New: Add unit testing phase
      - push-branch
      - create-pr
      - pr-review
```

## Error Messages

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `TOML001` | Invalid TOML syntax | Check quoting and table definitions |
| `TOML002` | Duplicate key | Remove duplicate entries |
| `BUILDER001` | Invalid builder type | Use `docker`, `nixpacks`, or `buildpack` |
| `PORT001` | Invalid port number | Use port in range 1-65535 |
| `HEALTH001` | Missing health check | Add health check configuration |
| `ENV001` | Invalid environment variable name | Use uppercase with underscores |
| `RESOURCE001` | Resource limit out of range | Adjust memory/CPU within limits |

## Related

- [Railway Config Generator](railway-config-generator.md)
- [Integration Tester](integration-tester.md)
- [TOML Specification](https://toml.io/en/)
- [Railway Documentation](https://docs.railway.app/)
