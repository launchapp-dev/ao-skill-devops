# Vercel Next.js Application Deployment Example

A production-ready Vercel configuration for Next.js applications with serverless functions, ISR support, and optimized edge caching.

## Input Specification

```yaml
# input.yaml
deployment_type: framework
framework: nextjs
regions:
  - iad1
  - sfo1
routes:
  - src: /api/(.*)
    dest: /api/$1
  - src: /(.*)
    dest: /$1
    headers:
      - x-custom-header: value
environment_variables:
  NODE_ENV: production
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
secret_environment_variables:
  - DATABASE_URL
  - API_SECRET_KEY
functions:
  api:
    memory: 1024
    maxDuration: 10
```

## Generated vercel.json

```json
{
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "regions": ["iad1", "sfo1"],
  "functions": {
    "api/**/*": {
      "memory": 1024,
      "maxDuration": 10,
      "runtime": "nodejs18.x"
    },
    "pages/api/revalidate/**": {
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
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  },
  "secrets": {
    "DATABASE_URL": "@database-url",
    "API_SECRET_KEY": "@api-secret-key"
  }
}
```

## Advanced Configuration Examples

### With Image Optimization

```json
{
  "version": 2,
  "framework": "nextjs",
  "images": {
    "domains": ["images.unsplash.com", "cdn.example.com"],
    "sizes": [640, 750, 828, 1080, 1200, 1920, 2048],
    "formats": ["image/avif", "image/webp"],
    "minimumCacheTTL": 60
  }
}
```

### With Incremental Static Regeneration

```json
{
  "version": 2,
  "framework": "nextjs",
  "routes": [
    {
      "src": "/blog/[slug]",
      "dest": "/blog/[slug]",
      "headers": {
        "Cache-Control": "s-maxage=60, stale-while-revalidate"
      }
    }
  ]
}
```

### With Edge Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Add security headers
  const response = NextResponse.next();
  
  response.headers.set('X-Custom-Header', 'value');
  response.headers.set(
    'Strict-Transport-Security',
    'max-age=63072000; includeSubDomains; preload'
  );
  
  // Redirect based on geolocation
  const country = request.geo?.country;
  if (country === 'US') {
    return NextResponse.redirect(new URL('/en-us' + request.nextUrl.pathname, request.url));
  }
  
  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

### With ISR Revalidation API

```typescript
// pages/api/revalidate.ts
import type { NextApiRequest, NextApiResponse } from 'next/server';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.query.secret !== process.env.REVALIDATION_SECRET) {
    return res.status(401).json({ message: 'Invalid token' });
  }

  try {
    const path = req.query.path as string;
    await res.revalidate(path);
    return res.json({ revalidated: true, path });
  } catch (err) {
    return res.status(500).json({ message: 'Error revalidating' });
  }
}
```

## Deployment Commands

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Deploy with specific regions
vercel --prod --regions iad1,sfo1,fra1

# Deploy with environment variables
vercel --prod -e DATABASE_URL=$DATABASE_URL
```

## Serverless Function Configuration

### Memory and Duration

```json
{
  "functions": {
    "api/process": {
      "memory": 3008,
      "maxDuration": 60
    },
    "api/export": {
      "memory": 1024,
      "maxDuration": 30
    }
  }
}
```

### Node.js Runtime Options

```json
{
  "functions": {
    "api/**/*": {
      "runtime": "nodejs18.x",
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

## Environment Variables

```bash
# Production secrets
vercel secrets add database-url "postgresql://..."
vercel secrets add api-secret-key "sk-xxx"

# Add to project
vercel env add DATABASE_URL production
vercel env add API_SECRET_KEY production

# Pull to local
vercel env pull .env.local
```

## Monitoring and Analytics

```bash
# View function logs
vercel logs my-project

# View specific function
vercel logs my-project --follow --only-fn api/process

# Enable Analytics
vercel analytics enable
```

## Troubleshooting

```bash
# View deployment details
vercel inspect deployment-url

# Redeploy specific commit
vercel --prod --force

# Clear build cache
vercel rm build-cache
```
