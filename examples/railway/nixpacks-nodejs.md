# Railway Nixpacks Node.js Deployment Example

A production-ready Railway deployment using Nixpacks for automatic Node.js build configuration with health checks and environment variables.

## Input Specification

```yaml
# input.yaml
deployment_type: nixpacks
language: nodejs
build_command: npm run build
start_command: npm start
port: 3000
healthcheck_path: /health
environment_variables:
  NODE_ENV: production
secret_variables:
  - DATABASE_URL
  - REDIS_URL
```

## Generated railway.toml

```toml
[deployment]
  name = "myapp"
  buildType = "nixpacks"

[nixpacks]
  language = "nodejs"
  languageVersion = "20"
  buildCommand = "npm run build"
  startCommand = "npm start"

[container]
  port = 3000
  healthcheckPath = "/health"
  healthcheckInterval = 30
  healthcheckTimeout = 5
  healthcheckRetries = 3

[resources]
  memory = "512 MB"
  cpu = "1 vCPU"

[environment]
  NODE_ENV = "production"
```

## Nixpacks Configuration File

```toml
# nixpacks.toml
providers = ["nodejs"]

[phases.setup]
nixpkgsArchive = "22.11"

[phases.build]
cmds = ["npm install", "npm run build"]

[start]
cmd = "npm start"
```

## Supported Node.js Versions

```toml
[nixpacks]
  language = "nodejs"
  languageVersion = "20"  # Options: 16, 18, 20, 21, current, lts, latest
```

## Environment Variables

```bash
# Set via CLI
railway variables set NODE_ENV=production
railway variables set API_URL=https://api.example.com

# Reference Railway secrets
railway secrets add DATABASE_URL
railway secrets add REDIS_URL
railway secrets add API_SECRET

# List variables
railway variables
```

## Health Check Implementation

```typescript
// src/health.ts
import express from 'express';

const router = express.Router();

interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: number;
  uptime: number;
  checks: {
    database: boolean;
    redis: boolean;
  };
}

router.get('/health', async (req, res) => {
  const status: HealthStatus = {
    status: 'healthy',
    timestamp: Date.now(),
    uptime: process.uptime(),
    checks: {
      database: await checkDatabase(),
      redis: await checkRedis()
    }
  };

  const allHealthy = Object.values(status.checks).every(v => v);
  
  res.status(allHealthy ? 200 : 503).json(status);
});

router.get('/ready', async (req, res) => {
  const dbReady = await checkDatabase();
  const redisReady = await checkRedis();
  
  if (dbReady && redisReady) {
    res.status(200).json({ status: 'ready' });
  } else {
    res.status(503).json({ 
      status: 'not ready',
      database: dbReady,
      redis: redisReady
    });
  }
});

export default router;
```

## Package.json Configuration

Railway automatically detects your `package.json`:

```json
{
  "name": "myapp",
  "version": "1.0.0",
  "scripts": {
    "dev": "nodemon",
    "build": "tsc && npm run copy-assets",
    "start": "node dist/index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.0",
    "redis": "^4.6.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.17",
    "typescript": "^5.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

## Deployment Commands

```bash
# Initialize and deploy
railway init
railway up

# Deploy with specific environment
railway up --environment production

# Deploy from subdirectory
railway up --path ./apps/api

# View deployment logs
railway logs

# Open in browser
railway open
```

## Database Integration

```bash
# Add PostgreSQL
railway add postgresql

# The DATABASE_URL will be automatically set
railway variables get DATABASE_URL

# Add Redis
railway add redis
railway variables get REDIS_URL
```

### Automatic Connection Example

```typescript
// src/db.ts
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

export async function checkDatabase(): Promise<boolean> {
  try {
    await pool.query('SELECT 1');
    return true;
  } catch {
    return false;
  }
}

export default pool;
```

## Custom Build Commands

### With Build Arguments

```toml
[nixpacks]
  language = "nodejs"
  languageVersion = "20"
  buildCommand = "npm install --legacy-peer-deps && npm run build"
  startCommand = "npm start"

[env]
  NPM_CONFIG_PRODUCTION = "false"
```

### With Prisma

```toml
[nixpacks]
  language = "nodejs"
  buildCommand = "npm install && npx prisma generate && npm run build"
  startCommand = "npx prisma migrate deploy && npm start"
```

### With Build Output Directory

```toml
[nixpacks]
  language = "nodejs"
  buildCommand = "npm run build"
  startCommand = "node server.js"
```

## Memory and CPU Configuration

```toml
[resources]
  memory = "1024 MB"  # Options: 256 MB, 512 MB, 1 GB, 2 GB, 4 GB
  cpu = "2"           # Options: 0.25, 0.5, 1, 2, 4, 8
```

## Troubleshooting

### Build Failures

```bash
# View detailed build logs
railway buildlogs

# Check for errors in package.json
cat package.json | jq '.scripts'

# Verify build command works locally
npm run build
```

### Runtime Issues

```bash
# View application logs
railway logs --tail 100

# Check environment variables
railway variables

# Test locally with same env
railway run npm start
```

## Performance Optimization

### Connection Pooling

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

### Caching with Redis

```typescript
import { createClient } from 'redis';

const redis = createClient({
  url: process.env.REDIS_URL
});

await redis.connect();

// Cache with TTL
await redis.setEx('key', 3600, JSON.stringify(data));

// Get cached
const cached = await redis.get('key');
```
