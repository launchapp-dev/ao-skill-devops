# Kubernetes Manifests Generator

A specialized agent for generating Kubernetes manifests and configurations.

## Features

- **Deployment Manifests**: Generate Deployment YAML with replicas, containers, probes, resource limits
- **Service Manifests**: ClusterIP, NodePort, and LoadBalancer service types
- **Ingress Manifests**: Ingress resources with rules, paths, and TLS configuration
- **ConfigMap Manifests**: Key-value pairs and file-based configs
- **Secret Manifests**: Opaque, kubernetes.io/tls, and other secret types
- **PersistentVolumeClaim**: Storage requests with access modes
- **Helm Chart Patterns**: values.yaml templates and chart structure
- **Kustomize Overlays**: base/overlays directory structure

## Usage

### Direct Agent Invocation

```yaml
agent: k8s-manifest-agent
input:
  manifest_type: deployment
  name: my-application
  namespace: production
  replicas: 3
  image: myregistry/myapp:v1.2.3
  ports:
    - name: http
      containerPort: 8080
      servicePort: 80
  env:
    - name: DATABASE_URL
      value: postgres://db:5432/app
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### Generated Output

The agent produces valid Kubernetes YAML that can be applied directly:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-application
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-application
  template:
    metadata:
      labels:
        app: my-application
    spec:
      containers:
        - name: my-application
          image: myregistry/myapp:v1.2.3
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: DATABASE_URL
              value: postgres://db:5432/app
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

## Helm Chart Support

Generate complete Helm chart structure:

```yaml
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

## Kustomize Support

Generate Kustomize overlay structure:

```yaml
input:
  manifest_type: kustomize
  base_chart: ./base
  overlays:
    - name: dev
      replicas: 1
      image_tag: dev
    - name: prod
      replicas: 5
      image_tag: stable
```

## Validation

The agent can optionally validate manifests using:
- kubeval
- kubectl --dry-run=client
- kubeconform

## Best Practices

1. Always specify namespace explicitly
2. Use labels consistently for selector matching
3. Set resource requests and limits
4. Configure health probes (liveness/readiness)
5. Use ConfigMaps for configuration, Secrets for sensitive data
6. Follow Kubernetes naming conventions
