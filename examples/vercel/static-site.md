# Vercel Static Site Deployment Example

A production-ready Vercel configuration for deploying static sites with optimized caching, custom headers, and global distribution.

## Input Specification

```yaml
# input.yaml
deployment_type: static
build_command: npm run build
output_directory: dist
environment_variables:
  NODE_ENV: production
```

## Generated vercel.json

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": null,
  "regions": ["iad1", "sfo1", "fra1"],
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "headers": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
      }
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-DNS-Prefetch-Control",
          "value": "on"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        }
      ]
    },
    {
      "source": "/sw.js",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-cache, no-store, must-revalidate"
        },
        {
          "key": "Service-Worker-Allowed",
          "value": "/"
        }
      ]
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

## Deployment Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Deploy with environment variables
vercel --prod -e NODE_ENV=production

# Link to existing project
vercel link
vercel env pull .env.local
```

## Configuration for Specific Static Site Generators

### For Create React App

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "installCommand": "npm install",
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### For Next.js Static Export

```json
{
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": "out",
  "installCommand": "npm install"
}
```

### For Astro

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "astro"
}
```

### For SvelteKit with Static Adapter

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "installCommand": "npm install",
  "framework": "sveltekit"
}
```

## Cache Optimization

### Immutable Assets

```json
{
  "routes": [
    {
      "src": "/_next/static/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/images/(.*)",
      "headers": {
        "Cache-Control": "public, max-age=86400, stale-while-revalidate=604800"
      }
    }
  ]
}
```

## Security Headers

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
```

## Domain Configuration

```bash
# Add custom domain
vercel domains add example.com

# Configure domain
vercel domains config example.com

# List domains
vercel domains ls
```

## Environment Variables

```bash
# Add environment variable
vercel env add NODE_ENV production

# List environment variables
vercel env ls

# Pull to local
vercel env pull .env.local
```

## Monitoring

```bash
# View deployment logs
vercel logs my-deployment

# View inspections
vercel inspect deployment-id

# List deployments
vercel ls
```
