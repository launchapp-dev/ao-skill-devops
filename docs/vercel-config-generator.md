# Vercel Config Generator

A specialized agent for generating Vercel deployment configurations.

## Features

- **Static Sites**: Pre-built HTML/CSS/JS deployments
- **Serverless Functions**: Node.js API routes with configurable limits
- **Edge Functions**: Low-latency global deployments
- **Monorepo Support**: Multi-package repository configurations
- **Framework Presets**: Next.js, Nuxt, SvelteKit, Astro, Remix, Expo
- **Route Configuration**: Headers, redirects, rewrites
- **Environment Variables**: Static and secret-based configuration
- **Region Deployment**: Single or multi-region configurations

## Usage

### Direct Agent Invocation

```yaml
agent: vercel-config-agent
input:
  deployment_type: serverless
  framework: nextjs
  regions:
    -iad1
    - sfo1
  build_command: npm run build
  output_directory: .next
  environment_variables:
    NODE_ENV: production
  secret_environment_variables:
    - DATABASE_URL
    - API_KEY
  routes:
    - src: /api/(.*)
      dest: /api/$1
    - src: /(.*)
      dest: /$1
      headers:
        - x-custom-header: value
  functions:
    api:
      runtime: nodejs18.x
      memory: 1024
      maxDuration: 10
```

### Generated Output

The agent produces valid `vercel.json` that can be deployed directly:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1",
      "headers": {
        "x-custom-header": "value"
      }
    }
  ],
  "env": {
    "NODE_ENV": "production"
  },
  "functions": {
    "api/**/*.ts": {
      "runtime": "nodejs18.x",
      "memory": 1024,
      "maxDuration": 10
    }
  }
}
```

## Deployment Types

### Static Site

```yaml
input:
  deployment_type: static
  build_command: npm run build
  output_directory: dist
  environment_variables:
    NODE_ENV: production
```

### Serverless API

```yaml
input:
  deployment_type: serverless
  framework: nodejs
  build_command: npm run build
  functions:
    api:
      runtime: nodejs18.x
      memory: 1024
      maxDuration: 30
  environment_variables:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Next.js Application

```yaml
input:
  deployment_type: framework
  framework: nextjs
  regions:
    -iad1
    - sfo1
    - cdg1
  routes:
    - src: /api/(.*)
      dest: /api/$1
```

### Monorepo

```yaml
input:
  deployment_type: monorepo
  regions:
    -iad1
  functions:
    api:
      memory: 512
      maxDuration: 30
  environment_variables:
    NODE_ENV: production
```

## Framework Presets

| Framework | Builder | Notes |
|-----------|---------|-------|
| nextjs | @vercel/next | Auto page routing |
| nuxt | @vercel/nft | Nuxt universal rendering |
| sveltekit | @vercel/static | SvelteKit adapters |
| astro | @vercel/static | Static/SSR |
| remix | @vercel/remix | Full-stack |
| expo | @vercel/go | React Native |
| nodejs | @vercel/node | Serverless functions |

## Function Configuration Options

- **runtime**: Node.js runtime version (nodejs18.x, nodejs16.x)
- **memory**: Memory allocation in MB (128-3008)
- **maxDuration**: Maximum execution time in seconds (1-900)
- **regions**: Deployment regions (iad1, sfo1, cdg1, etc.)

## Environment Variables

### Static Variables

```yaml
environment_variables:
  NODE_ENV: production
  API_URL: https://api.example.com
```

### Secret Variables

```yaml
secret_environment_variables:
  - DATABASE_URL
  - API_KEY
  - STRIPE_SECRET
```

## Route Configuration

### Headers

```yaml
routes:
  - src: /(.*)
    headers:
      - x-custom-header: value
      - Cache-Control: public, max-age=3600
```

### Redirects

```yaml
routes:
  - src: /old-path
    dest: /new-path
    status: 307  # Temporary redirect
  - src: /moved
    dest: /new-location
    status: 308  # Permanent redirect
```

### Rewrites

```yaml
routes:
  - src: /api/proxy/(.*)
    dest: https://external-api.com/$1
  - src: /blog/(.*)
    dest: /blog-post?id=$1
```

## Validation

The agent validates generated configurations:

- JSON syntax correctness
- Valid Vercel version field (must be 2)
- Valid function runtimes
- Valid region codes
- Valid route patterns
- Proper environment variable naming

## Best Practices

1. Always specify explicit regions for latency optimization
2. Use `${{ secrets.VAR }}` for sensitive values
3. Configure proper cache headers for static assets
4. Set appropriate `maxDuration` for long-running functions
5. Use trailing slash consistently in routes
6. Configure CORS headers for API routes
7. Use incremental static regeneration for dynamic content
