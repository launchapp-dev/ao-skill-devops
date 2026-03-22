# ao-skill-devops

A skill pack for generating Kubernetes manifests, GitHub Actions workflows, Dockerfiles, and deployment configurations automatically.

## Features

- **Kubernetes Manifest Generator**: Generate Deployment, Service, Ingress, ConfigMap, Secret, and PVC manifests
- **Helm Chart Support**: Create complete Helm chart structures
- **Kustomize Overlays**: Generate multi-environment configurations
- **GitHub Actions Workflows**: CI/CD pipeline templates

## Installation

This skill pack integrates with the AO (Agent Orchestrator) daemon. Install by referencing the pack:

```toml
# In your project's pack.toml or via AO CLI
[skills]
exports = [
  "ao.devops/k8s-manifest-generator",
]
```

## Quick Start

### Generate a Kubernetes Deployment

```yaml
agent: k8s-manifest-agent
input:
  manifest_type: deployment
  name: my-app
  namespace: production
  replicas: 3
  image: myregistry/myapp:v1.0.0
  ports:
    - name: http
      containerPort: 8080
      servicePort: 80
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### Generate a Helm Chart

```yaml
agent: k8s-manifest-agent
input:
  manifest_type: helm
  chart_name: my-chart
  values:
    replicaCount: 2
    image:
      repository: myapp
      tag: latest
    service:
      type: ClusterIP
      port: 80
```

## Examples Gallery

Comprehensive examples with realistic use cases are available in the [`examples/`](examples/) directory:

### Language-Specific Examples

- **[Node.js](examples/nodejs/)**: Express.js REST API, Bull queue workers
- **[Python](examples/python/)**: FastAPI async services, Django with Celery
- **[Go](examples/go/)**: HTTP servers, gRPC microservices
- **[Multi-Service](examples/multi-service/)**: Full web stacks, microservices platforms

### Example Contents

Each example includes:
- **Input specification** (YAML) for the generator
- **Generated manifests** (Deployment, Service, ConfigMap, etc.)
- **Best practices** for production deployments
- **Additional configurations** (HPA, Ingress, health checks)

## Supported Manifest Types

| Type | Description |
|------|-------------|
| `deployment` | Deployment with replicas, containers, probes |
| `service` | ClusterIP, NodePort, LoadBalancer services |
| `ingress` | HTTP routing with TLS and rules |
| `configmap` | Configuration key-value pairs |
| `secret` | Sensitive data storage |
| `pvc` | Persistent volume claims |
| `helm` | Complete Helm chart structure |
| `kustomize` | Base/overlays directory structure |

## Documentation

- [Kubernetes Manifest Generator](docs/k8s-manifest-generator.md)
- [Examples Gallery](examples/README.md)

## Workflows

This skill pack provides the following workflows:

| Workflow | Description |
|----------|-------------|
| `ao.devops/standard` | Plan → Implement → Push → PR → Review |
| `ao.devops/quick-fix` | Implement → Push → PR |
| `ao.devops/k8s-manifest` | Generate manifests → Push → PR → Review |

## Best Practices

1. **Always specify namespace**: Don't rely on the default namespace
2. **Set resource limits**: Prevent runaway resource consumption
3. **Configure health probes**: Ensure proper pod lifecycle management
4. **Use secrets for sensitive data**: Never hardcode credentials
5. **Use labels consistently**: Enable proper selector matching

## License

MIT
