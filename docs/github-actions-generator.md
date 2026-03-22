# GitHub Actions Generator

A specialized agent for generating GitHub Actions workflows for CI/CD pipelines.

## Features

- **Multi-Language Support**: Node.js, Python, and Go environments
- **CI Workflows**: Lint, test, build steps with caching
- **CD Workflows**: Docker build/push and deployment
- **Matrix Builds**: Parallel testing across OS and versions
- **Dependency Caching**: Optimized build times
- **Artifact Handling**: Upload and download build artifacts
- **Docker Support**: Multi-stage builds and registry push

## Supported Environments

### Node.js

- **Versions**: 16.x, 18.x, 20.x, 22.x
- **Package Managers**: npm, yarn, pnpm
- **Linters**: ESLint, Prettier
- **Test Frameworks**: Jest, Mocha, Vitest
- **Build Tools**: webpack, esbuild, TypeScript

### Python

- **Versions**: 3.9, 3.10, 3.11, 3.12
- **Package Managers**: pip, poetry, pipenv
- **Linters**: pylint, flake8, ruff, black
- **Test Frameworks**: pytest, unittest

### Go

- **Versions**: 1.19, 1.20, 1.21, 1.22
- **Linters**: golangci-lint
- **Test Framework**: go test
- **Build Tools**: go build, goreleaser

## Usage

### Generate Node.js CI Workflow

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

### Generate Python CI/CD with Docker

```yaml
agent: github-actions-agent
input:
  environment: python
  workflow_type: ci-cd
  name: Python CI/CD
  language_version: "3.11"
  steps:
    - lint
    - test
    - build
    - docker
  cache: true
  docker:
    image_name: myregistry/myapp
    dockerfile: ./Dockerfile
```

### Generate Go CD Pipeline

```yaml
agent: github-actions-agent
input:
  environment: go
  workflow_type: cd
  name: Go CD Pipeline
  language_version: "1.21"
  steps:
    - test
    - build
    - docker
  cache: true
  artifact:
    name: binary
    path: ./dist
```

## Generated Output Example

For a Node.js CI workflow with matrix builds:

```yaml
name: Node.js CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: ["18.x", "20.x"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.os }}-${{ matrix.node-version }}
          path: dist/
```

## Workflow Types

### CI (Continuous Integration)

- Code linting
- Unit testing
- Build verification
- Artifact generation
- Multi-version/multi-platform testing

### CD (Continuous Deployment)

- Docker image building
- Registry push
- Deployment execution
- Environment-specific configs

### CI-CD (Full Pipeline)

- Combines CI and CD features
- Conditional deployments
- Multi-stage workflows

## Matrix Builds

Configure parallel builds across different platforms:

```yaml
matrix:
  os: [ubuntu-latest, macos-latest, windows-latest]
  node-version: ["18.x", "20.x"]
  exclude:
    - os: macos-latest
      node-version: "18.x"
```

## Caching Strategies

| Environment | Cache Target |
|-------------|--------------|
| Node.js | `npm/yarn/pnpm` cache directory |
| Python | `pip/poetry` cache directory |
| Go | `Go module cache` |

## Best Practices

1. **Always specify versions**: Pin language versions for reproducibility
2. **Use caching**: Speed up builds with dependency caching
3. **Add timeouts**: Prevent runaway jobs with sensible timeouts
4. **Use matrix builds**: Test across multiple versions/platforms
5. **Artifact retention**: Set appropriate retention periods
6. **Concurrency controls**: Prevent duplicate workflow runs
7. **Security**: Use secrets for sensitive data, never hardcode

## Validation

The agent generates syntactically valid GitHub Actions YAML that conforms to:
- Official GitHub Actions workflow schema
- Best practices for workflow structure
- Security recommendations
