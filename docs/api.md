# API Documentation

This document provides detailed API documentation for programmatic usage of the ao-skill-devops skill pack.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [AO CLI Usage](#ao-cli-usage)
- [JavaScript/TypeScript SDK](#javascripttypescript-sdk)
- [Python SDK](#python-sdk)
- [Skill Reference](#skill-reference)
- [Workflow Reference](#workflow-reference)
- [Type Definitions](#type-definitions)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

The ao-skill-devops skill pack provides programmatic APIs for generating DevOps configurations. You can use it via:

1. **AO CLI** - Command-line interface
2. **JavaScript/TypeScript SDK** - Node.js package
3. **Python SDK** - Python package
4. **REST API** - HTTP API (when deployed as a service)

## Installation

### AO CLI

```bash
npm install -g @launchapp-dev/ao-cli
```

### JavaScript/TypeScript SDK

```bash
npm install @launchapp-dev/ao-skill-devops
# or
yarn add @launchapp-dev/ao-skill-devops
# or
pnpm add @launchapp-dev/ao-skill-devops
```

### Python SDK

```bash
pip install ao-skill-devops
# or
poetry add ao-skill-devops
```

## AO CLI Usage

### Basic Commands

```bash
# List available generators
ao devops list

# Generate a configuration
ao devops generate <generator> --input <yaml-file>

# Generate with inline input
ao devops generate dockerfile --input '{"language": "nodejs", "build_type": "multistage"}'

# Generate and save to file
ao devops generate k8s --input input.yaml --output deployment.yaml

# Validate generated output
ao devops validate <file>

# Run generator tests
ao devops test <generator>
```

### Generator Commands

```bash
# Dockerfile generation
ao devops dockerfile --input input.yaml --output Dockerfile

# Kubernetes manifest generation
ao devops k8s --manifest deployment --input input.yaml --output deployment.yaml

# GitHub Actions generation
ao devops github-actions --input input.yaml --output .github/workflows/ci.yaml

# Docker Compose generation
ao devops compose --input input.yaml --output docker-compose.yaml

# Railway config generation
ao devops railway --input input.yaml --output railway.toml

# Vercel config generation
ao devops vercel --input input.yaml --output vercel.json
```

### Workflow Commands

```bash
# Run a workflow
ao devops workflow run --workflow <workflow-id> --task-id <task-id>

# List workflows
ao devops workflow list

# Get workflow status
ao devops workflow status <workflow-id>
```

## JavaScript/TypeScript SDK

### Initialize Client

```typescript
import { AoDevops } from '@launchapp-dev/ao-skill-devops';

const client = new AoDevops({
  apiKey: process.env.AO_API_KEY,
  baseUrl: 'https://api.ao.dev', // Optional, for REST API
});

// Or with default configuration
const client = new AoDevops();
```

### Generate Dockerfiles

```typescript
import { DockerfileGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new DockerfileGenerator();

const result = await generator.generate({
  buildType: 'multistage',
  language: 'nodejs',
  languageVersion: '20.x',
  buildCommand: 'npm run build',
  startCommand: 'npm start',
  port: 3000,
  healthcheck: {
    cmd: 'curl -f http://localhost:3000/health || exit 1',
    interval: '30s',
    timeout: '5s',
    retries: 3,
    startPeriod: '40s',
  },
  environmentVariables: {
    NODE_ENV: 'production',
  },
  user: 'node',
});

console.log(result.dockerfile);
```

### Generate Kubernetes Manifests

```typescript
import { K8sManifestGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new K8sManifestGenerator();

const result = await generator.generate({
  manifestType: 'deployment',
  name: 'my-application',
  namespace: 'production',
  replicas: 3,
  image: 'myregistry/myapp:v1.2.3',
  ports: [
    {
      name: 'http',
      containerPort: 8080,
      servicePort: 80,
    },
  ],
  resources: {
    requests: {
      memory: '256Mi',
      cpu: '100m',
    },
    limits: {
      memory: '512Mi',
      cpu: '500m',
    },
  },
});

console.log(result.manifest);
```

### Generate GitHub Actions

```typescript
import { GitHubActionsGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new GitHubActionsGenerator();

const result = await generator.generate({
  environment: 'nodejs',
  workflowType: 'ci',
  name: 'Node.js CI',
  languageVersion: '20.x',
  steps: ['lint', 'test', 'build'],
  cache: true,
  matrix: {
    os: ['ubuntu-latest', 'macos-latest'],
    nodeVersion: ['18.x', '20.x'],
  },
});

console.log(result.workflow);
```

### Generate Docker Compose

```typescript
import { DockerComposeGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new DockerComposeGenerator();

const result = await generator.generate({
  composeVersion: '3.8',
  services: [
    {
      name: 'api',
      build: {
        context: '.',
        dockerfile: 'Dockerfile',
      },
      ports: ['3000:3000'],
      environment: {
        DATABASE_URL: 'postgres://postgres:secret@db:5432/myapp',
        NODE_ENV: 'production',
      },
      dependsOn: ['db', 'redis'],
      healthcheck: {
        test: 'curl -f http://localhost:3000/health || exit 1',
        interval: '30s',
        timeout: '10s',
        retries: 3,
      },
      restart: 'unless-stopped',
    },
    {
      name: 'db',
      image: 'postgres:15-alpine',
      environment: {
        POSTGRES_USER: 'postgres',
        POSTGRES_PASSWORD: 'secret',
        POSTGRES_DB: 'myapp',
      },
      volumes: ['db_data:/var/lib/postgresql/data'],
    },
    {
      name: 'redis',
      image: 'redis:7-alpine',
      volumes: ['redis_data:/data'],
    },
  ],
  networks: [
    { name: 'backend', driver: 'bridge' },
  ],
  volumes: [
    { name: 'db_data' },
    { name: 'redis_data' },
  ],
});

console.log(result.compose);
```

### Generate Railway Config

```typescript
import { RailwayConfigGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new RailwayConfigGenerator();

const result = await generator.generate({
  deploymentType: 'docker',
  dockerfilePath: 'Dockerfile',
  dockerContext: '.',
  port: 8080,
  numReplicas: 2,
  healthcheckPath: '/health',
  healthcheckInterval: 30,
  healthcheckTimeout: 5,
  healthcheckRetries: 3,
  environmentVariables: {
    NODE_ENV: 'production',
    PORT: '8080',
  },
  secretVariables: ['DATABASE_URL', 'API_KEY'],
  memoryLimit: 512,
  cpu: 1,
});

console.log(result.config);
```

### Generate Vercel Config

```typescript
import { VercelConfigGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new VercelConfigGenerator();

const result = await generator.generate({
  deploymentType: 'serverless',
  framework: 'nextjs',
  regions: ['iad1', 'sfo1'],
  buildCommand: 'npm run build',
  outputDirectory: '.next',
  environmentVariables: {
    NODE_ENV: 'production',
  },
  secretEnvironmentVariables: ['DATABASE_URL', 'API_KEY'],
  routes: [
    {
      src: '/api/(.*)',
      dest: '/api/$1',
    },
  ],
  functions: {
    api: {
      runtime: 'nodejs18.x',
      memory: 1024,
      maxDuration: 10,
    },
  },
});

console.log(result.config);
```

### Generate Python CI

```typescript
import { PythonCiGenerator } from '@launchapp-dev/ao-skill-devops';

const generator = new PythonCiGenerator();

const result = await generator.generate({
  environment: 'python',
  name: 'Python CI',
  version: '3.11',
  packageManager: 'poetry',
  coverageThreshold: 80,
  failUnder: 80,
  lint: true,
  linter: 'ruff',
  cache: true,
});

console.log(result.workflow);
```

### Run Integration Tests

```typescript
import { IntegrationTester } from '@launchapp-dev/ao-skill-devops';

const tester = new IntegrationTester();

const result = await tester.run({
  testType: 'config',
  targetConfig: './output/deployment.yaml',
  validationLevel: 'strict',
});

console.log(result.passed);
console.log(result.errors);
```

## Python SDK

### Initialize Client

```python
from ao_skill_devops import AoDevops

client = AoDevops(api_key=os.environ.get("AO_API_KEY"))
```

### Generate Dockerfiles

```python
from ao_skill_devops import DockerfileGenerator

generator = DockerfileGenerator()

result = generator.generate(
    build_type="multistage",
    language="nodejs",
    language_version="20.x",
    build_command="npm run build",
    start_command="npm start",
    port=3000,
    healthcheck={
        "cmd": "curl -f http://localhost:3000/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3,
    },
    environment_variables={"NODE_ENV": "production"},
    user="node",
)

print(result.dockerfile)
```

### Generate Kubernetes Manifests

```python
from ao_skill_devops import K8sManifestGenerator

generator = K8sManifestGenerator()

result = generator.generate(
    manifest_type="deployment",
    name="my-application",
    namespace="production",
    replicas=3,
    image="myregistry/myapp:v1.2.3",
    ports=[
        {
            "name": "http",
            "container_port": 8080,
            "service_port": 80,
        }
    ],
    resources={
        "requests": {"memory": "256Mi", "cpu": "100m"},
        "limits": {"memory": "512Mi", "cpu": "500m"},
    },
)

print(result.manifest)
```

### Generate GitHub Actions

```python
from ao_skill_devops import GitHubActionsGenerator

generator = GitHubActionsGenerator()

result = generator.generate(
    environment="nodejs",
    workflow_type="ci",
    name="Node.js CI",
    language_version="20.x",
    steps=["lint", "test", "build"],
    cache=True,
    matrix={
        "os": ["ubuntu-latest", "macos-latest"],
        "node_version": ["18.x", "20.x"],
    },
)

print(result.workflow)
```

## Skill Reference

### Common Input Schema

All generators accept these common options:

```typescript
interface CommonOptions {
  // Optional custom output format
  outputFormat?: 'yaml' | 'json' | 'toml';

  // Whether to include comments in output
  includeComments?: boolean;

  // Validation strictness level
  validationLevel?: 'strict' | 'moderate' | 'lenient';

  // Additional generator-specific options
  options?: Record<string, unknown>;
}
```

### Return Types

All generators return:

```typescript
interface GeneratorResult<T> {
  // The generated configuration
  content: T;

  // Validation warnings
  warnings: ValidationWarning[];

  // Metadata about the generation
  metadata: {
    generator: string;
    version: string;
    generatedAt: string;
    inputHash: string;
  };
}

interface ValidationWarning {
  message: string;
  field?: string;
  severity: 'warning' | 'info';
  suggestion?: string;
}
```

## Workflow Reference

### Run Workflow

```typescript
import { WorkflowRunner } from '@launchapp-dev/ao-skill-devops';

const runner = new WorkflowRunner();

const result = await runner.run({
  workflowId: 'ao.devops/standard',
  taskId: 'TASK-001',
  input: {
    // Workflow-specific input
  },
});

console.log(result.status);
console.log(result.phases);
```

### Available Workflows

| Workflow ID | Description |
|-------------|-------------|
| `ao.devops/standard` | Plan → Implement → Push → PR → Review |
| `ao.devops/quick-fix` | Implement → Push → PR |
| `ao.devops/k8s-manifest` | Generate K8s manifests → Push → PR → Review |
| `ao.devops/standard-with-tests` | Plan → Implement → Test → Push → PR |
| `ao.devops/github-actions` | Generate GitHub Actions workflows |
| `ao.devops/python-ci` | Generate Python CI with pytest |
| `ao.devops/vercel-config` | Generate Vercel deployment configs |
| `ao.devops/railway-config` | Generate Railway deployment configs |
| `ao.devops/dockerfile` | Generate production Dockerfiles |
| `ao.devops/docker-compose` | Generate docker-compose files |

## Type Definitions

### Dockerfile Generator Types

```typescript
interface DockerfileInput {
  buildType: 'multistage' | 'single-stage' | 'scratch' | 'distroless';
  language: 'nodejs' | 'python' | 'go' | 'rust' | 'deno' | 'bun' | 'static' | 'other';
  languageVersion?: string;
  buildCommand?: string;
  startCommand?: string;
  outputDirectory?: string;
  workingDirectory?: string;
  port?: number;
  baseImage?: string;
  builderImage?: string;
  finalImage?: string;
  buildArguments?: Record<string, string>;
  environmentVariables?: Record<string, string>;
  secrets?: string[];
  healthcheck?: HealthcheckConfig;
  user?: string;
  labels?: Record<string, string>;
  copyFiles?: CopyFileConfig[];
  optimizeCache?: boolean;
  minimizeLayers?: boolean;
  options?: Record<string, unknown>;
}

interface HealthcheckConfig {
  cmd: string;
  interval?: string;
  timeout?: string;
  retries?: number;
  startPeriod?: string;
}
```

### Kubernetes Generator Types

```typescript
interface K8sManifestInput {
  manifestType: 'deployment' | 'service' | 'ingress' | 'configmap' | 'secret' | 'pvc' | 'helm' | 'kustomize';
  name: string;
  namespace?: string;
  spec?: ManifestSpec;
  options?: Record<string, unknown>;
}

interface ManifestSpec {
  replicas?: number;
  image?: string;
  ports?: PortConfig[];
  env?: EnvVar[];
  resources?: ResourceRequirements;
  volumes?: Volume[];
  // ... other fields based on manifest type
}
```

### GitHub Actions Generator Types

```typescript
interface GitHubActionsInput {
  environment: 'nodejs' | 'python' | 'go';
  workflowType: 'ci' | 'cd' | 'ci-cd';
  name: string;
  version?: string;
  languageVersion?: string;
  steps?: ('lint' | 'test' | 'build' | 'docker' | 'deploy')[];
  cache?: boolean;
  matrix?: MatrixConfig;
  artifact?: ArtifactConfig;
  docker?: DockerConfig;
  options?: Record<string, unknown>;
}

interface MatrixConfig {
  os?: string[];
  [key: string]: string[] | undefined;
}
```

## Error Handling

### Error Types

```typescript
// All SDK methods throw these error types

class AoDevopsError extends Error {
  code: string;
  details?: Record<string, unknown>;
}

class ValidationError extends AoDevopsError {
  validationErrors: ValidationErrorDetail[];
}

class GenerationError extends AoDevopsError {
  generator: string;
  reason: string;
}

class AuthenticationError extends AoDevopsError {
  // Invalid or missing API key
}

class RateLimitError extends AoDevopsError {
  retryAfter: number;
}
```

### Error Handling Example

```typescript
import { 
  AoDevopsError, 
  ValidationError, 
  GenerationError 
} from '@launchapp-dev/ao-skill-devops';

try {
  const result = await generator.generate(input);
} catch (error) {
  if (error instanceof ValidationError) {
    console.error('Validation failed:');
    error.validationErrors.forEach(err => {
      console.error(`  - ${err.field}: ${err.message}`);
    });
  } else if (error instanceof GenerationError) {
    console.error(`Generation failed: ${error.reason}`);
  } else if (error instanceof AoDevopsError) {
    console.error(`API error: ${error.code} - ${error.message}`);
  } else {
    throw error;
  }
}
```

## Examples

### Complete Workflow Example

```typescript
import { 
  AoDevops, 
  DockerfileGenerator, 
  K8sManifestGenerator, 
  GitHubActionsGenerator 
} from '@launchapp-dev/ao-skill-devops';

async function deployMicroservice() {
  const client = new AoDevops();

  // 1. Generate Dockerfile
  const dockerfileGen = new DockerfileGenerator();
  const dockerfile = await dockerfileGen.generate({
    buildType: 'multistage',
    language: 'nodejs',
    languageVersion: '20.x',
    buildCommand: 'npm run build',
    startCommand: 'npm start',
    port: 3000,
    healthcheck: {
      cmd: 'curl -f http://localhost:3000/health || exit 1',
      interval: '30s',
      timeout: '5s',
      retries: 3,
    },
    environmentVariables: {
      NODE_ENV: 'production',
    },
    user: 'node',
  });

  // 2. Generate Kubernetes manifests
  const k8sGen = new K8sManifestGenerator();
  const deployment = await k8sGen.generate({
    manifestType: 'deployment',
    name: 'my-microservice',
    namespace: 'production',
    replicas: 3,
    image: 'myregistry/myapp:v1.0.0',
    ports: [
      { name: 'http', containerPort: 3000, servicePort: 80 },
    ],
    resources: {
      requests: { memory: '256Mi', cpu: '100m' },
      limits: { memory: '512Mi', cpu: '500m' },
    },
  });

  const service = await k8sGen.generate({
    manifestType: 'service',
    name: 'my-microservice',
    namespace: 'production',
    spec: {
      type: 'ClusterIP',
      ports: [{ port: 80, targetPort: 3000 }],
    },
  });

  // 3. Generate GitHub Actions CI
  const githubGen = new GitHubActionsGenerator();
  const ci = await githubGen.generate({
    environment: 'nodejs',
    workflowType: 'ci-cd',
    name: 'CI/CD Pipeline',
    languageVersion: '20.x',
    steps: ['lint', 'test', 'build', 'docker'],
    cache: true,
    docker: {
      imageName: 'myregistry/myapp',
      dockerfile: './Dockerfile',
    },
  });

  return {
    dockerfile: dockerfile.content,
    deployment: deployment.content,
    service: service.content,
    ciWorkflow: ci.content,
  };
}
```

### Batch Generation Example

```typescript
import { BatchGenerator } from '@launchapp-dev/ao-skill-devops';

const batch = new BatchGenerator();

// Generate multiple configurations in parallel
const results = await batch.generateAll([
  {
    generator: 'dockerfile',
    input: { language: 'nodejs', buildType: 'multistage' },
    outputFile: 'Dockerfile',
  },
  {
    generator: 'k8s',
    input: { manifestType: 'deployment', name: 'app' },
    outputFile: 'k8s/deployment.yaml',
  },
  {
    generator: 'github-actions',
    input: { environment: 'nodejs', workflowType: 'ci' },
    outputFile: '.github/workflows/ci.yaml',
  },
]);

// Check results
for (const result of results) {
  if (result.success) {
    console.log(`Generated: ${result.outputFile}`);
  } else {
    console.error(`Failed: ${result.error}`);
  }
}
```
