# Railway Monorepo Deployment Example

A production-ready Railway deployment configuration for monorepo architectures with multiple services using both Docker and Nixpacks.

## Input Specification

```yaml
# input.yaml
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
    healthcheck_path: /
```

## Generated railway.toml (Root)

```toml
[deployment]
  name = "myapp-monorepo"

[project]
  id = "your-project-id"
```

## Per-Service Configurations

### services/api/railway.toml

```toml
[deployment]
  name = "api"
  path = "./services/api"
  dockerfilePath = "./services/api/Dockerfile"
  numReplicas = 2

[container]
  port = 4000
  healthcheckPath = "/health"
  healthcheckInterval = 30
  healthcheckTimeout = 5
  healthcheckRetries = 3

[resources]
  memory = "1024 MB"
  cpu = "1 vCPU"
```

### services/worker/railway.toml

```toml
[deployment]
  name = "worker"
  path = "./services/worker"
  buildType = "nixpacks"

[nixpacks]
  language = "nodejs"
  languageVersion = "20"
  buildCommand = "npm install && npm run build"
  startCommand = "npm start:worker"

[resources]
  memory = "512 MB"
  cpu = "0.5 vCPU"
```

### apps/web/railway.toml

```toml
[deployment]
  name = "web"
  path = "./apps/web"
  buildType = "nixpacks"

[nixpacks]
  language = "nodejs"
  languageVersion = "20"
  buildCommand = "npm install && npm run build"
  startCommand = "npm start"

[container]
  port = 3000
  healthcheckPath = "/"
  healthcheckInterval = 30
  healthcheckTimeout = 5
  healthcheckRetries = 3

[resources]
  memory = "256 MB"
  cpu = "0.5 vCPU"
```

## Monorepo Structure

```
my-project/
├── apps/
│   └── web/                 # Frontend application
│       ├── package.json
│       ├── railway.toml
│       └── src/
├── services/
│   ├── api/                 # Backend API
│   │   ├── Dockerfile
│   │   ├── railway.toml
│   │   └── src/
│   └── worker/              # Background worker
│       ├── package.json
│       ├── railway.toml
│       └── src/
├── packages/
│   └── shared/              # Shared libraries
│       └── src/
├── railway.toml             # Root config
└── package.json             # Workspace root
```

## Root package.json

```json
{
  "name": "my-project",
  "private": true,
  "workspaces": [
    "apps/*",
    "services/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "deploy": "turbo run deploy"
  },
  "devDependencies": {
    "turbo": "^1.10.0"
  }
}
```

## Deployment via CLI

```bash
# Link to project
railway link

# Deploy all services
railway up

# Deploy specific service
railway up --service api

# Deploy from path
railway up --service api --path ./services/api

# Deploy multiple services
railway up --service api,worker,web

# View all services
railway status

# View service logs
railway logs --service api
railway logs --service worker
```

## Service Discovery

Services can communicate via Railway's internal networking:

### API Service

```typescript
// services/api/src/config.ts
export const config = {
  // Worker URL (Railway internal)
  workerUrl: process.env.WORKER_URL || 'http://worker:4001',
  
  // Database
  databaseUrl: process.env.DATABASE_URL,
  
  // Redis
  redisUrl: process.env.REDIS_URL,
  
  // RabbitMQ
  rabbitmqUrl: process.env.RABBITMQ_URL,
};
```

### Worker Service

```typescript
// services/worker/src/index.ts
const config = {
  // API URL
  apiUrl: process.env.API_URL || 'http://api:4000',
  
  // Database
  databaseUrl: process.env.DATABASE_URL,
  
  // Redis (also used for job queue)
  redisUrl: process.env.REDIS_URL,
};
```

## Shared Environment Variables

### Root railway.toml (Variables)

```bash
# Set shared variables via CLI
railway variables set REDIS_URL=$REDIS_URL
railway variables set RABBITMQ_URL=$RABBITMQ_URL

# These will be available to all services
```

### services/api/.env.example

```env
# Database
DATABASE_URL=

# Redis (shared across services)
REDIS_URL=

# RabbitMQ (shared across services)
RABBITMQ_URL=

# Service URLs (set by Railway)
WORKER_URL=
WEB_URL=

# API specific
API_PORT=4000
JWT_SECRET=
```

## Inter-Service Communication

### HTTP Communication

```typescript
// services/api/src/clients/worker.ts
import fetch from 'node-fetch';

export async function notifyWorker(job: Job): Promise<void> {
  const response = await fetch(`${process.env.WORKER_URL}/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Internal-Request': 'true',
    },
    body: JSON.stringify(job),
  });
  
  if (!response.ok) {
    throw new Error(`Worker notification failed: ${response.status}`);
  }
}
```

### Message Queue (Bull with Redis)

```typescript
// services/worker/src/queue.ts
import Queue from 'bull';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL!);

export const jobQueue = new Queue('jobs', {
  redis: {
    host: redis.options.host,
    port: redis.options.port,
    password: redis.options.password,
  },
});

jobQueue.process(async (job) => {
  console.log(`Processing job ${job.id}`);
  // Process job...
});
```

## Scaling Configuration

### API Service (Higher resources)

```toml
[deployment]
  numReplicas = 3

[resources]
  memory = "2048 MB"
  cpu = "2 vCPU"
```

### Worker Service (Lower resources)

```toml
[deployment]
  numReplicas = 5

[resources]
  memory = "512 MB"
  cpu = "0.5 vCPU"
```

## Database Schema Migrations

### API Service

```toml
[nixpacks]
  language = "nodejs"
  buildCommand = "npm install && npm run build && npm run db:migrate"
  startCommand = "npm start"
```

### Migrations Script

```json
{
  "scripts": {
    "db:migrate": "prisma migrate deploy",
    "db:seed": "prisma db seed"
  }
}
```

## Monitoring

```bash
# View all service statuses
railway status

# View logs for specific service
railway logs api --tail 100
railway logs worker --follow

# View metrics
railway metrics --service api

# View deployment history
railway deployments --service worker
```

## Troubleshooting

```bash
# Check service health
railway healthcheck api

# View service configuration
railway variables --service api

# Redeploy specific service
railway redeploy --service worker

# Rollback service
railway rollback --service api
```

## Common Patterns

### API Gateway Pattern

```nginx
# services/gateway/nginx.conf
upstream api {
    server api:4000;
}

upstream web {
    server web:3000;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://web;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

### Background Job Pattern

```typescript
// services/worker/src/index.ts
import Queue from 'bull';
import { createClient } from 'redis';

const redis = createClient(process.env.REDIS_URL!);
const jobQueue = new Queue('jobs', { redis: redis });

// Process jobs with retries
jobQueue.process(async (job, done) => {
  try {
    const result = await processJob(job.data);
    done(null, result);
  } catch (error) {
    done(error);
  }
});

// Retry failed jobs
jobQueue.on('failed', async (job, err) => {
  console.error(`Job ${job.id} failed:`, err);
  await job.retry();
});
```
