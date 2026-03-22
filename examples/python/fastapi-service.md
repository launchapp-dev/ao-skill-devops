# Python FastAPI Service Example

A high-performance async REST API built with FastAPI, featuring automatic OpenAPI documentation and async database support.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: fastapi-service
namespace: production
replicas: 4
image: myregistry/fastapi-service:v3.0.0
ports:
  - name: http
    containerPort: 8000
    servicePort: 80
  - name: grpc
    containerPort: 50051
    servicePort: 50051
env:
  - name: ENVIRONMENT
    value: production
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: fastapi-config
    configMapKey: REDIS_URL
  - name: LOG_LEVEL
    value: INFO
  - name: WORKERS
    value: "4"
  - name: MAX_CONNECTIONS
    value: "100"
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
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "2000m"
```

## Generated Manifests

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-service
  namespace: production
  labels:
    app: fastapi-service
    version: v3.0.0
spec:
  replicas: 4
  selector:
    matchLabels:
      app: fastapi-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: fastapi-service
        version: v3.0.0
    spec:
      containers:
        - name: fastapi-service
          image: myregistry/fastapi-service:v3.0.0
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
            - name: grpc
              containerPort: 50051
              protocol: TCP
          env:
            - name: ENVIRONMENT
              value: production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: fastapi-config
                  key: REDIS_URL
            - name: LOG_LEVEL
              value: INFO
            - name: WORKERS
              value: "4"
            - name: MAX_CONNECTIONS
              value: "100"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              memory: 512Mi
              cpu: 500m
            limits:
              memory: 1Gi
              cpu: 2000m
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
      restartPolicy: Always
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
  namespace: production
  labels:
    app: fastapi-service
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: grpc
      port: 50051
      targetPort: grpc
  selector:
    app: fastapi-service
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
  namespace: production
  labels:
    app: fastapi-service
data:
  REDIS_URL: "redis://redis:6379/0"
  CACHE_TTL: "300"
  API_RATE_LIMIT: "100/minute"
  CORS_ORIGINS: "https://app.example.com"
```

### HorizontalPodAutoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-service
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-service
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
```

## FastAPI-Specific Features

### Database Connection Pooling

```python
# asyncpg configuration
DATABASE_URL = "postgresql+asyncpg://user:pass@postgres:5432/db"
```

### Health Check Implementation

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def liveness():
    return {"status": "ok"}

@app.get("/ready")
async def readiness():
    # Check database connection
    await check_db_connection()
    return {"status": "ready"}
```
