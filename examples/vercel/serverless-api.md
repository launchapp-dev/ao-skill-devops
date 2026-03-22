# Vercel Serverless API Deployment Example

A production-ready Vercel configuration for deploying serverless Node.js APIs with timeout controls, memory settings, and proper CORS configuration.

## Input Specification

```yaml
# input.yaml
deployment_type: serverless
framework: nodejs
build_command: npm run build
functions:
  api:
    runtime: nodejs18.x
    memory: 1024
    maxDuration: 10
environment_variables:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  REDIS_URL: ${{ secrets.REDIS_URL }}
secret_environment_variables:
  - DATABASE_URL
  - REDIS_URL
  - API_SECRET_KEY
```

## Generated vercel.json

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": null,
  "regions": ["iad1"],
  "functions": {
    "api/**/*.js": {
      "memory": 1024,
      "maxDuration": 10,
      "runtime": "nodejs18.x"
    },
    "api/heavy-process.js": {
      "memory": 3008,
      "maxDuration": 60
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://your-frontend.com"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization, X-Request-ID"
        },
        {
          "key": "Access-Control-Max-Age",
          "value": "86400"
        }
      ]
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

## API Handler Examples

### Basic Express API

```typescript
// api/index.js
import express from 'express';
import cors from 'cors';

const app = express();

app.use(cors({
  origin: 'https://your-frontend.com',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: Date.now() });
});

app.get('/api/users', async (req, res) => {
  try {
    const users = await getUsers();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

app.post('/api/users', async (req, res) => {
  try {
    const { name, email } = req.body;
    const user = await createUser({ name, email });
    res.status(201).json(user);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create user' });
  }
});

module.exports = app;
```

### Lambda-compatible Handler

```typescript
// api/handler.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  const { method, url, headers, query, body } = req;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Route handling
  const path = url?.split('?')[0];
  
  switch (path) {
    case '/api/health':
      return res.json({ status: 'ok' });
    
    case '/api/data':
      if (method === 'GET') {
        return res.json({ data: await fetchData() });
      }
      if (method === 'POST') {
        return res.json({ created: await createRecord(body) });
      }
      break;
    
    default:
      return res.status(404).json({ error: 'Not found' });
  }
}
```

### Heavy Processing Endpoint

```typescript
// api/heavy-process.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

// This endpoint uses more memory and longer timeout
export const config = {
  runtime: 'nodejs18.x',
  memory: 3008,
  maxDuration: 60,
};

export default async function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  // Heavy computation or data processing
  const result = await processLargeDataset();
  
  return res.json({
    success: true,
    processed: result.count,
    duration: result.duration
  });
}
```

## API Key Authentication

```typescript
// lib/auth.ts
import type { VercelRequest } from '@vercel/node';

export function authenticateRequest(req: VercelRequest): boolean {
  const apiKey = req.headers['x-api-key'];
  return apiKey === process.env.API_SECRET_KEY;
}

export function requireAuth(handler: Function) {
  return async (req: VercelRequest, res: VercelResponse) => {
    if (!authenticateRequest(req)) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    return handler(req, res);
  };
}
```

## Deployment Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Deploy specific function
vercel --prod --force

# Deploy with secrets
vercel secrets add database-url "postgresql://..."
vercel --prod
```

## Testing Locally

```bash
# Install Vercel CLI
npm i -g vercel

# Run local server
vercel dev

# Test specific endpoint
curl http://localhost:3000/api/health
```

## Rate Limiting Implementation

```typescript
// lib/rateLimit.ts
const rateLimit = new Map();

export function checkRateLimit(
  identifier: string,
  limit: number = 100,
  windowMs: number = 60000
): boolean {
  const now = Date.now();
  const windowStart = now - windowMs;
  
  // Get existing requests
  const requests = rateLimit.get(identifier) || [];
  
  // Filter out old requests
  const recentRequests = requests.filter(time => time > windowStart);
  
  if (recentRequests.length >= limit) {
    return false;
  }
  
  // Add current request
  recentRequests.push(now);
  rateLimit.set(identifier, recentRequests);
  
  return true;
}

// Usage in handler
export default async function handler(req: VercelRequest, res: VercelResponse) {
  const identifier = req.headers['x-forwarded-for'] || 'unknown';
  
  if (!checkRateLimit(identifier, 100, 60000)) {
    res.setHeader('Retry-After', '60');
    return res.status(429).json({ error: 'Too many requests' });
  }
  
  // Process request...
}
```

## Monitoring and Debugging

```bash
# View function logs
vercel logs my-project

# Follow logs in real-time
vercel logs my-project --follow

# Filter by function
vercel logs my-project --only-fn api/index

# View deployment details
vercel inspect deployment-url
```

## Performance Tips

1. **Connection Pooling**: Reuse database connections
2. **Response Caching**: Cache frequent responses at edge
3. **Payload Size**: Keep request/response payloads small
4. **Async Operations**: Use Promise.all for parallel operations
5. **Cold Starts**: Minimize imports, lazy-load heavy modules
