# CLI Generator Interface

A unified command-line interface for invoking DevOps generators in the ao-skill-devops skill pack.

## Overview

The CLI interface provides a consistent, user-friendly way to invoke all DevOps generators through a single command structure. It supports both interactive mode (with guided prompts) and non-interactive mode (for CI/CD pipelines and scripting).

## Installation

```bash
# Install via npm
npm install -g @launchapp/ao-skill-devops

# Or use directly with npx
npx ao-devops <command>
```

## Quick Start

### Interactive Mode

Run without any arguments to enter interactive mode:

```bash
ao-devops
```

You'll see a menu of available generators:

```
╔══════════════════════════════════════════════════════════════════╗
║              ao-devops - DevOps Generator CLI                    ║
╠══════════════════════════════════════════════════════════════════╣
║  Welcome! Select a generator to create:                          ║
║                                                                  ║
║  [1] GitHub Actions   - CI/CD workflows                         ║
║  [2] Dockerfile       - Container images                         ║
║  [3] docker-compose   - Multi-service orchestration              ║
║  [4] Vercel           - Serverless deployment                   ║
║  [5] Railway          - Railway deployment                       ║
║  [6] Kubernetes       - K8s manifests                           ║
║  [7] .env example     - Environment variables                   ║
║  [8] Python CI        - Python testing workflows               ║
║  [9] All generators   - Generate complete stack                 ║
║                                                                  ║
║  [H] Help                    [Q] Quit                           ║
╚══════════════════════════════════════════════════════════════════╝

Select option:
```

### Non-Interactive Mode

Generate configurations directly with command-line arguments:

```bash
# GitHub Actions
ao-devops github-actions --environment nodejs --name "My CI" --cache

# Dockerfile
ao-devops dockerfile --language nodejs --multistage --healthcheck

# docker-compose
ao-devops docker-compose --services api,db,redis --output docker-compose.yml

# Vercel
ao-devops vercel --type serverless --framework nextjs

# Railway
ao-devops railway --type docker --port 3000

# Kubernetes
ao-devops kubernetes --manifest deployment --name myapp --port 8080

# .env example
ao-devops env --framework nodejs --database --auth

# Python CI
ao-devops python-ci --framework fastapi --coverage 80
```

## Command Structure

```
ao-devops [global-flags] <subcommand> [subcommand-flags] [arguments]
```

### Global Flags

| Flag | Alias | Description |
|------|-------|-------------|
| `--help` | `-h` | Show help for any command |
| `--version` | `-v` | Show version information |
| `--interactive` | `-i` | Force interactive mode |
| `--non-interactive` | `-n` | Disable interactive mode |
| `--output <path>` | `-o` | Output file path |
| `--format <format>` | | Output format (json, yaml, toml, env) |
| `--dry-run` | | Show what would be generated |
| `--verbose` | `-vv` | Enable verbose output |
| `--quiet` | `-q` | Suppress non-essential output |
| `--config <path>` | `-c` | Path to config file |
| `--no-input` | `-y` | Skip all prompts |

### Subcommands

#### github-actions (gh-actions, gha)

Generate GitHub Actions CI/CD workflows.

```bash
ao-devops github-actions [flags]

Flags:
  -e, --environment <env>    Build environment (nodejs, python, go)
  -n, --name <name>          Workflow name
  -V, --version <version>    Language version
  --cache                    Enable dependency caching
  --matrix                   Enable matrix builds
  --docker                   Include Docker build/push
```

**Examples:**

```bash
# Basic Node.js CI
ao-devops github-actions -e nodejs -n "Node CI"

# Python with matrix
ao-devops gh-actions -e python -n "Python Tests" --matrix

# Go with Docker
ao-devops gha -e go -n "Go CI/CD" --docker
```

#### dockerfile (docker)

Generate production-ready Dockerfiles.

```bash
ao-devops dockerfile [flags]

Flags:
  -l, --language <lang>      Language (nodejs, python, go, rust, etc.)
  -V, --version <version>    Language version
  --multistage                Use multi-stage build
  --healthcheck               Add health check
  -p, --port <port>          Application port
```

**Examples:**

```bash
# Node.js multi-stage
ao-devops dockerfile -l nodejs --multistage --healthcheck

# Python with gunicorn
ao-devops docker -l python -V 3.12 -p 8000
```

#### docker-compose (compose, dc)

Generate docker-compose.yml files.

```bash
ao-devops docker-compose [flags]

Flags:
  -s, --services <list>      Comma-separated services
  -o, --output <path>        Output file path
```

**Examples:**

```bash
# API with database
ao-devops docker-compose -s api,postgres,redis

# Full stack
ao-devops compose -s api,web,db,redis,cache --output docker-compose.prod.yml
```

#### vercel

Generate Vercel deployment configurations.

```bash
ao-devops vercel [flags]

Flags:
  -t, --type <type>          Deployment type (static, serverless, edge)
  -f, --framework <fw>       Framework (nextjs, nuxt, etc.)
```

**Examples:**

```bash
# Next.js serverless
ao-devops vercel -t serverless -f nextjs

# Static site
ao-devops vercel --type static
```

#### railway

Generate Railway deployment configurations.

```bash
ao-devops railway [flags]

Flags:
  -t, --type <type>          Deployment type (docker, nixpacks)
  -p, --port <port>          Application port
```

**Examples:**

```bash
# Docker deployment
ao-devops railway -t docker -p 3000

# Nixpacks auto-detect
ao-devops railway --type nixpacks
```

#### kubernetes (k8s, k8)

Generate Kubernetes manifests.

```bash
ao-devops kubernetes [flags]

Flags:
  -m, --manifest <type>      Manifest type (deployment, service, ingress, etc.)
  -n, --name <name>          Resource name
  -p, --port <port>          Container port
```

**Examples:**

```bash
# Deployment
ao-devops kubernetes -m deployment -n myapp -p 8080

# Service
ao-devops k8s -m service -n myapp --port 8080

# All manifests
ao-devops k8 -m all -n myapp
```

#### env (env-example, dotenv)

Generate .env.example files.

```bash
ao-devops env [flags]

Flags:
  -f, --framework <fw>       Framework (nodejs, python, etc.)
  --database                  Include database variables
  --cache                     Include cache variables
  --auth                      Include auth variables
  --storage                   Include storage variables
```

**Examples:**

```bash
# Node.js with database
ao-devops env -f nodejs --database --auth

# Python full stack
ao-devops env --framework python --database --cache --storage
```

#### python-ci

Generate Python CI workflows with pytest and coverage.

```bash
ao-devops python-ci [flags]

Flags:
  -f, --framework <fw>       Framework (django, fastapi, etc.)
  --coverage <percent>        Minimum coverage threshold
  --linter <linter>           Linter (ruff, pylint, etc.)
```

**Examples:**

```bash
# FastAPI with 80% coverage
ao-devops python-ci -f fastapi --coverage 80

# Django with ruff
ao-devops python-ci --framework django --linter ruff
```

#### all

Generate all configurations at once.

```bash
ao-devops all [flags]

Flags:
  -p, --preset <preset>      Preset (fullstack, microservices, etc.)
  --stack <stack>            Tech stack (nodejs-postgres, python-redis, etc.)
```

**Examples:**

```bash
# Fullstack Node.js
ao-devops all --preset fullstack

# Microservices
ao-devops all --preset microservices

# Custom stack
ao-devops all --stack nodejs-postgres-redis
```

## Input Formats

### JSON Input

```bash
# From stdin
echo '{"environment":"nodejs","name":"CI"}' | ao-devops github-actions --json -

# From file
ao-devops github-actions --input config.json

# Inline
ao-devops github-actions --json '{"environment":"python","cache":true}'
```

### YAML Input

```bash
# From file
ao-devops github-actions --input config.yaml

# Inline
ao-devops github-actions --yaml "environment: nodejs\nname: CI"
```

### Config File

Create `.ao-devops.yaml` in your project root:

```yaml
# .ao-devops.yaml
default_environment: nodejs
output_dir: ./config

github_actions:
  name: "My Workflow"
  cache: true

dockerfile:
  multistage: true
  healthcheck: true

env:
  framework: nodejs
  database: true
  auth: true
```

Then run:

```bash
ao-devops github-actions --config .ao-devops.yaml
```

## Output Formats

### Default Output

Each generator writes to its standard location:

| Generator | Default Path |
|-----------|-------------|
| github-actions | `.github/workflows/` |
| dockerfile | `Dockerfile` |
| docker-compose | `docker-compose.yml` |
| vercel | `vercel.json` |
| railway | `railway.toml` |
| kubernetes | `k8s/` |
| env | `.env.example` |

### Custom Output

```bash
# Specific file
ao-devops github-actions -e nodejs -o .github/workflows/node-ci.yml

# Stdout
ao-devops dockerfile -l nodejs --stdout

# JSON for piping
ao-devops kubernetes -m deployment -n myapp --format json | jq '.spec'
```

### Dry Run

Preview without writing:

```bash
ao-devops github-actions -e nodejs --dry-run
```

Output:

```
[DRY RUN] Would generate: .github/workflows/nodejs-ci.yml
---
name: Node.js CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
...
---
```

## Interactive Mode Features

### Guided Prompts

Each prompt shows:
- Clear description of the option
- Default value in brackets
- Validation feedback
- Help available with `?`

### Menu Navigation

```
╔════════════════════════════════════════════════════════════╗
║  Step 2: Configure GitHub Actions                          ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Environment: [nodejs     ]                                ║
║  Workflow name: [My CI     ]                              ║
║  Enable caching? [Yes]                                    ║
║                                                            ║
║  [Enter] Continue  [B] Back  [H] Help  [Q] Quit           ║
╚════════════════════════════════════════════════════════════╝
```

### Preview Before Write

```
Generated configuration:

┌────────────────────────────────────────────────────────────┐
│ .github/workflows/ci.yml                                   │
├────────────────────────────────────────────────────────────┤
│ name: My CI                                                │
│ on: push, pull_request                                     │
│ jobs:                                                      │
│   build:                                                   │
│     runs-on: ubuntu-latest                                 │
│     steps:                                                 │
│       - uses: actions/checkout@v4                          │
│       - uses: actions/setup-node@v4                        │
│         with:                                              │
│           node-version: '20'                               │
│       - run: npm ci                                       │
│       - run: npm test                                     │
└────────────────────────────────────────────────────────────┘

[Enter] Save to file  [P] Preview full  [E] Edit  [C] Cancel
```

## Error Handling

### Missing Required Options

```bash
$ ao-devops github-actions
Error: --environment (-e) is required
Help: ao-devops github-actions --help
```

### Invalid Values

```bash
$ ao-devops github-actions --environment ruby
Error: Invalid environment 'ruby'. Valid: nodejs, python, go
Help: ao-devops github-actions --help
```

### File Conflicts

Interactive mode:

```
Warning: Dockerfile already exists
Options: [O]verwrite, [S]kip, [B]ackup, [Q]uit
>
```

Non-interactive mode:

```bash
$ ao-devops dockerfile --language nodejs
Error: Dockerfile already exists
Use --output to specify a different path, or use --non-interactive to skip
```

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(ao-devops --completion bash)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(ao-devops --completion zsh)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
ao-devops --completion fish | source
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Validation error |
| 4 | File write error |
| 5 | Configuration error |

## Examples in CI/CD

### GitHub Actions

```yaml
# .github/workflows/generate.yml
name: Generate DevOps Config

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate all configs
        run: |
          npx ao-devops all --preset fullstack --non-interactive
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add -A
          git diff --staged --quiet || git commit -m "chore: update DevOps configs"
          git push
```

### GitLab CI

```yaml
# .gitlab-ci.yml
generate-configs:
  stage: generate
  image: node:20-alpine
  script:
    - npx ao-devops all --preset fullstack --non-interactive
  artifacts:
    paths:
      - .github/workflows/
      - Dockerfile
      - docker-compose.yml
      - .env.example
```

## Presets

### Available Presets

| Preset | Description | Generators |
|--------|-------------|------------|
| `fullstack` | Frontend + Backend + Database | github-actions, dockerfile, docker-compose, env |
| `microservices` | Multiple services with orchestration | All generators |
| `static` | Static site deployment | github-actions, vercel, env |
| `api` | API service only | github-actions, dockerfile, k8s |
| `nodejs` | Node.js application | github-actions, dockerfile, env |
| `python` | Python application | github-actions, python-ci, dockerfile, env |

### Stack Presets

| Stack | Environment | Services |
|-------|-------------|----------|
| `nodejs-postgres` | nodejs | api, postgres |
| `nodejs-postgres-redis` | nodejs | api, postgres, redis |
| `python-postgres` | python | api, postgres |
| `python-redis` | python | api, redis |
| `go-postgres` | go | api, postgres |

## See Also

- [GitHub Actions Generator](./github-actions-generator.md)
- [Dockerfile Generator](./dockerfile-generator.md)
- [Docker Compose Generator](./docker-compose-generator.md)
- [Vercel Config Generator](./vercel-config-generator.md)
- [Railway Config Generator](./railway-config-generator.md)
- [Kubernetes Manifest Generator](./k8s-manifest-generator.md)
- [Environment Example Generator](./env-example-generator.md)
