# Railway Docker Deployment Example

A production-ready Railway deployment configuration using Docker with health checks, replica scaling, and environment variables.

## Input Specification

```yaml
# input.yaml
deployment_type: docker
dockerfile_path: Dockerfile
docker_context: .
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

## Generated railway.toml

```toml
[deployment]
  name = "myapp"
  dockerfilePath = "Dockerfile"
  dockerContext = "."
  numReplicas = 2

[container]
  port = 8080
  healthcheckPath = "/health"
  healthcheckInterval = 30
  healthcheckTimeout = 5
  healthcheckRetries = 3

[container.probes]
  liveness = "/health"
  readiness = "/ready"

[resources]
  memory = "512 MB"
  cpu = "1 vCPU"

[environment]
  NODE_ENV = "production"
  PORT = "8080"
```

## Railway.json Alternative

```json
{
  "deployment": {
    "name": "myapp",
    "dockerfilePath": "Dockerfile",
    "dockerContext": ".",
    "numReplicas": 2
  },
  "container": {
    "port": 8080,
    "healthcheckPath": "/health",
    "healthcheckInterval": 30,
    "healthcheckTimeout": 5,
    "healthcheckRetries": 3
  },
  "resources": {
    "memory": 512,
    "cpu": 1
  }
}
```

## Deployment via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project
railway link

# Deploy
railway up

# Deploy specific file
railway up --dockerfile ./Dockerfile.production

# View logs
railway logs

# Open dashboard
railway open

# Add environment variables
railway variables set NODE_ENV=production
railway variables set DATABASE_URL=$DATABASE_URL

# Add secrets
railway secrets add DATABASE_URL
railway secrets add API_KEY
```

## Environment Variables Configuration

### Using railway.toml

```toml
[environment]
  NODE_ENV = "production"
  PORT = "8080"
  LOG_LEVEL = "info"

[environment.secrets]
  # These will be pulled from Railway secrets
  DATABASE_URL = "@DATABASE_URL"
  API_KEY = "@API_KEY"
```

### Via Dashboard

1. Go to Railway dashboard
2. Select your project
3. Navigate to Variables
4. Add key-value pairs or reference secrets

## Health Check Implementation

```typescript
// Node.js health check endpoint
const express = require('express');
const app = express();

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

// Readiness check (optional)
app.get('/ready', async (req, res) => {
  try {
    await checkDatabaseConnection();
    await checkRedisConnection();
    res.status(200).json({ status: 'ready' });
  } catch (error) {
    res.status(503).json({ status: 'not ready', error: error.message });
  }
});
```

## Scaling Configuration

```toml
[deployment]
  name = "myapp"
  dockerfilePath = "Dockerfile"
  numReplicas = 4
```

### Autoscaling (Coming Soon)

```toml
[deployment]
  name = "myapp"
  dockerfilePath = "Dockerfile"
  autoscaling = true

[autoscaling]
  minReplicas = 1
  maxReplicas = 10
  cpuThreshold = 70
  memoryThreshold = 80
```

## Multi-Region Deployment

```toml
[deployment]
  name = "myapp"
  dockerfilePath = "Dockerfile"
  primaryRegion = "us-east"

[regions]
  enabled = ["us-east", "us-west", "eu-west"]
```

## Nixpacks Alternative

If not using a Dockerfile, Railway can auto-detect:

```toml
[deployment]
  name = "myapp"
  buildType = "nixpacks"

[nixpacks]
  language = "nodejs"
  buildCommand = "npm run build"
  startCommand = "npm start"

[container]
  port = 3000
```

## Database Integration

### PostgreSQL

```bash
# Create PostgreSQL database
railway add postgresql

# Get connection string
railway variables get DATABASE_URL
```

### Redis

```bash
# Add Redis plugin
railway add redis

# Get connection string
railway variables get REDIS_URL
```

## Monitoring

```bash
# View deployment status
railway status

# View logs
railway logs --follow

# View metrics
railway metrics

# View deployment history
railway deployments
```

## Troubleshooting

```bash
# Check build logs
railway buildlogs

# Check environment variables
railway variables

# Redeploy
railway redeploy

# Rollback to previous deployment
railway rollback
```
