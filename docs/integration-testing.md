# Integration Testing Infrastructure

This document describes the integration testing capabilities for the ao-skill-devops skill pack.

## Overview

The integration testing infrastructure provides end-to-end validation for generated DevOps configurations. It ensures that generated Kubernetes manifests, Dockerfiles, and GitHub Actions workflows are syntactically correct, follow best practices, and work as expected when applied.

## Components

### 1. Integration Tester Agent (`integration-tester-agent`)

The integration tester agent validates generated configurations through three testing categories:

#### CLI Tests
- Tests generated commands and scripts execute correctly
- Validates Docker build processes
- Simulates kubectl/helm operations
- Verifies script executability and dependencies

#### Config Validation
- **Kubernetes YAML**: Validates against official Kubernetes JSON schemas
- **GitHub Actions**: Validates workflow syntax against GitHub's schema
- **Dockerfile**: Checks syntax and best practices compliance
- **YAML/JSON Structure**: Ensures proper formatting and required fields

#### End-to-End Tests
- Simulates complete workflows with mocked external services
- Tests GitHub Actions with simulated events (PR, push, release)
- Validates deployment scenarios from start to finish
- Tests rollback and recovery procedures

### 2. Mock Services

The infrastructure includes mock implementations for external services:

| Mock Service | Purpose | Simulates |
|-------------|---------|-----------|
| GitHub API Mock | Simulates GitHub events | PR creation, push events, releases, status checks |
| Docker Registry Mock | Simulates image operations | Image push/pull, manifest retrieval |
| Kubernetes API Mock | Simulates cluster operations | kubectl apply, get, delete operations |

### 3. Test Workflows

Integration testing is available as a phase in the `ao.devops/standard-with-tests` and `ao.devops/k8s-manifest` workflows.

## Usage

### Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_type` | enum | Yes | Type of test: `cli`, `config`, `e2e`, or `all` |
| `target_config` | string | Yes | Path to the generated config file |
| `test_scenario` | string | No | Specific test scenario to run |
| `mock_mode` | boolean | No | Use mock services (default: true) |
| `validation_level` | enum | No | `strict`, `moderate`, or `lenient` (default: `moderate`) |

### Validation Levels

- **strict**: Enforce all schema requirements, fail on warnings
- **moderate**: Enforce schema, allow minor best practice issues
- **lenient**: Only check required fields and basic syntax

### Example Usage

```yaml
# Validate Kubernetes manifest
input:
  test_type: config
  target_config: ./output/deployment.yaml
  validation_level: strict

# End-to-end GitHub Actions test
input:
  test_type: e2e
  target_config: ./output/ci.yaml
  test_scenario: pr_opened
  mock_mode: true

# Docker build test
input:
  test_type: cli
  target_config: ./output/Dockerfile
  test_scenario: build_and_run
  mock_mode: false
```

## Output Format

Tests return structured results:

```json
{
  "passed": true,
  "duration_ms": 1523,
  "test_type": "config",
  "target_file": "./output/deployment.yaml",
  "errors": [],
  "warnings": [
    {
      "message": "Missing resource limits",
      "line": 45,
      "severity": "warning"
    }
  ],
  "mock_calls": [
    {
      "service": "kubernetes-api",
      "endpoint": "/api/v1/namespaces/default/pods",
      "called": false
    }
  ],
  "recommendations": [
    "Consider adding resource limits to container spec",
    "Add health check probes for better reliability"
  ]
}
```

## Best Practices

1. **Always run integration tests** after generating configurations
2. **Use mock services** in CI/CD environments to avoid external dependencies
3. **Set validation_level to strict** for production deployments
4. **Review recommendations** even when tests pass
5. **Clean up test artifacts** after test completion

## Integration with CI/CD

Add integration tests to your workflow:

```yaml
# In your CI/CD pipeline
- name: Run Integration Tests
  run: |
    ao workflow run --task-id ${{ env.TASK_ID }} \
      --workflow ao.devops/standard-with-tests
```

## Limitations

- Mock services may not perfectly simulate all external service behaviors
- Some tests require Docker or Kubernetes CLI tools to be installed
- End-to-end tests in real environments may have side effects
- Network-dependent tests may be flaky in CI/CD environments

## Related

- [Kubernetes Manifest Generator](k8s-manifest-generator.md)
- [Unit Testing (REQ-007)](../requirements/REQ-007.md)
