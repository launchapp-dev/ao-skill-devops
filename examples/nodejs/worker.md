# Node.js Worker Service Example

A background job processor using Bull queues with Redis, suitable for async workloads.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: worker-service
namespace: production
replicas: 2
image: myregistry/worker-service:v1.5.0
ports:
  - name: health
    containerPort: 8080
    servicePort: 8080
env:
  - name: NODE_ENV
    value: production
  - name: QUEUE_NAME
    value: jobs
  - name: REDIS_HOST
    value: redis-cluster
  - name: REDIS_PORT
    value: "6379"
  - name: WORKER_CONCURRENCY
    value: "5"
  - name: DATABASE_URL
    secretRef: db-credentials
    secretKey: DATABASE_URL
  - name: AWS_ACCESS_KEY_ID
    secretRef: aws-credentials
    secretKey: access-key
  - name: AWS_SECRET_ACCESS_KEY
    secretRef: aws-credentials
    secretKey: secret-key
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
  name: worker-service
  namespace: production
  labels:
    app: worker-service
    version: v1.5.0
    tier: worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: worker-service
  template:
    metadata:
      labels:
        app: worker-service
        version: v1.5.0
        tier: worker
    spec:
      containers:
        - name: worker-service
          image: myregistry/worker-service:v1.5.0
          ports:
            - name: health
              containerPort: 8080
              protocol: TCP
          env:
            - name: NODE_ENV
              value: production
            - name: QUEUE_NAME
              value: jobs
            - name: REDIS_HOST
              value: redis-cluster
            - name: REDIS_PORT
              value: "6379"
            - name: WORKER_CONCURRENCY
              value: "5"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DATABASE_URL
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-key
          resources:
            requests:
              memory: 512Mi
              cpu: 500m
            limits:
              memory: 1Gi
              cpu: 2000m
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
      restartPolicy: Always
      terminationGracePeriodSeconds: 60
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: worker-service
  namespace: production
  labels:
    app: worker-service
spec:
  type: ClusterIP
  ports:
    - name: health
      port: 8080
      targetPort: health
  selector:
    app: worker-service
```

## Worker Configuration

The worker service expects these environment variables:
- `REDIS_HOST`: Redis cluster hostname
- `REDIS_PORT`: Redis port (default: 6379)
- `QUEUE_NAME`: Bull queue name
- `WORKER_CONCURRENCY`: Number of concurrent jobs
