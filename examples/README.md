# Examples Gallery

This directory contains example templates and sample inputs/outputs for the Kubernetes Manifest Generator.

## Quick Start

Each language/framework has a complete example with:
- `input.yaml` - Sample input specification for the generator
- `deployment.yaml` - Expected generated Deployment manifest
- `service.yaml` - Expected generated Service manifest
- `configmap.yaml` - Optional ConfigMap for configuration
- `ingress.yaml` - Optional Ingress for HTTP routing

## Examples

### Node.js Applications
- [Express.js REST API](nodejs/express-api/) - Simple REST API with health checks
- [Node.js Worker Service](nodejs/worker/) - Background job processor with Redis

### Python Applications
- [FastAPI Service](python/fastapi-service/) - Async REST API with PostgreSQL
- [Django Application](python/django-app/) - Traditional Django app with Celery

### Go Applications
- [Go HTTP Server](go/http-server/) - High-performance HTTP server
- [Go gRPC Service](go/grpc-service/) - gRPC microservice with protobuf

### Multi-Service Applications
- [Web Application Stack](multi-service/web-app/) - Frontend + Backend + Database
- [E-commerce Platform](multi-service/ecommerce/) - Multiple microservices

## Usage

Generate manifests using the `ao.devops/k8s-manifest-generator` skill:

```yaml
agent: k8s-manifest-agent
input:
  manifest_type: deployment
  name: my-nodejs-app
  namespace: production
  replicas: 3
  image: myregistry/nodejs-app:v1.0.0
  ports:
    - name: http
      containerPort: 3000
      servicePort: 80
  env:
    - name: NODE_ENV
      value: production
    - name: PORT
      value: "3000"
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

See each example directory for complete specifications.
