# E-commerce Platform Example

A microservices-based e-commerce platform with catalog, orders, payments, and notification services.

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                           Kubernetes Cluster                           │
│                                                                         │
│  ┌─────────────┐                                                        │
│  │   Gateway   │                                                        │
│  │  (Kong/NG)  │                                                        │
│  └──────┬──────┘                                                        │
│         │                                                               │
│  ┌──────┴──────┬──────────────┬──────────────┐                         │
│  │             │              │              │                         │
│  ▼             ▼              ▼              ▼                         │
│ ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐                  │
│ │Catalog │ │ Orders │ │ Payments │ │ Notifications │                  │
│ │Service │ │Service │ │ Service  │ │    Service    │                  │
│ └───┬────┘ └───┬────┘ └────┬─────┘ └──────┬───────┘                  │
│     │           │           │              │                          │
│     └───────────┴───────────┴──────────────┘                          │
│                         │                                              │
│                   ┌─────┴─────┐                                        │
│                   │ PostgreSQL │                                        │
│                   │  Cluster  │                                        │
│                   └───────────┘                                        │
│                         │                                              │
│                   ┌─────┴─────┐                                        │
│                   │    Redis  │                                        │
│                   │   Cache   │                                        │
│                   └───────────┘                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Service Specifications

### API Gateway

```yaml
# gateway/input.yaml
manifest_type: deployment
name: api-gateway
namespace: production
replicas: 3
image: myregistry/api-gateway:v1.0.0
ports:
  - name: http
    containerPort: 8000
    servicePort: 80
  - name: admin
    containerPort: 8001
    servicePort: 8001
env:
  - name: LOG_LEVEL
    value: info
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

### Catalog Service

```yaml
# catalog-service/input.yaml
manifest_type: deployment
name: catalog-service
namespace: production
replicas: 3
image: myregistry/catalog-service:v2.0.0
ports:
  - name: http
    containerPort: 8080
    servicePort: 80
env:
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: common-config
    configMapKey: REDIS_URL
healthCheck:
  liveness:
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 20
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 10
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

### Orders Service

```yaml
# orders-service/input.yaml
manifest_type: deployment
name: orders-service
namespace: production
replicas: 3
image: myregistry/orders-service:v2.1.0
ports:
  - name: http
    containerPort: 8080
    servicePort: 80
env:
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: KAFKA_BROKERS
    configMapRef: orders-config
    configMapKey: KAFKA_BROKERS
  - name: JWT_SECRET
    secretRef: orders-secrets
    secretKey: JWT_SECRET
healthCheck:
  liveness:
    path: /health
    initialDelaySeconds: 15
    periodSeconds: 20
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 10
resources:
  requests:
    memory: "512Mi"
    cpu: "300m"
  limits:
    memory: "1Gi"
    cpu: "1500m"
```

### Payments Service

```yaml
# payments-service/input.yaml
manifest_type: deployment
name: payments-service
namespace: production
replicas: 2
image: myregistry/payments-service:v1.5.0
ports:
  - name: http
    containerPort: 8080
    servicePort: 80
env:
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: STRIPE_API_KEY
    secretRef: payments-secrets
    secretKey: STRIPE_API_KEY
  - name: WEBHOOK_SECRET
    secretRef: payments-secrets
    secretKey: WEBHOOK_SECRET
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Generated Manifests

### Catalog Service Deployment

```yaml
# catalog-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: catalog-service
  template:
    metadata:
      labels:
        app: catalog-service
    spec:
      containers:
        - name: catalog-service
          image: myregistry/catalog-service:v2.0.0
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: common-config
                  key: REDIS_URL
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: 256Mi
              cpu: 200m
            limits:
              memory: 512Mi
              cpu: 1000m
```

### Services

```yaml
# catalog-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: catalog-service
  namespace: production
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: catalog-service

---
# orders-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: orders-service
  namespace: production
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: orders-service

---
# payments-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-service
  namespace: production
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: payments-service
```

### Gateway Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-gateway
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: ecommerce-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /catalog(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: catalog-service
                port:
                  name: http
          - path: /orders(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: orders-service
                port:
                  name: http
          - path: /payments(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: payments-service
                port:
                  name: http
```

### Common ConfigMap

```yaml
# common-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: common-config
  namespace: production
data:
  REDIS_URL: "redis://redis-cluster:6379/0"
  KAFKA_BROKERS: "kafka-0:9092,kafka-1:9092,kafka-2:9092"
  CACHE_TTL: "300"
  RATE_LIMIT: "1000/minute"
```

## Horizontal Pod Autoscaling

```yaml
# catalog-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: catalog-service
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: catalog-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80

---
# orders-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orders-service
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orders-service
  minReplicas: 3
  maxReplicas: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Pods
      pods:
        metric:
          name: orders_per_second
        target:
          type: AverageValue
          averageValue: "100"
```

## Database Schema

```sql
-- Catalog database
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    inventory_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders database
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Payments database
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```
