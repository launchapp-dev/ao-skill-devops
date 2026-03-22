# Node.js Express.js REST API Example

A production-ready Node.js Express.js application with health checks, logging, and proper resource limits.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: express-api
namespace: production
replicas: 3
image: myregistry/express-api:v2.1.0
ports:
  - name: http
    containerPort: 3000
    servicePort: 80
  - name: metrics
    containerPort: 9090
    servicePort: 9090
env:
  - name: NODE_ENV
    value: production
  - name: PORT
    value: "3000"
  - name: LOG_LEVEL
    value: info
  - name: DATABASE_URL
    secretRef: db-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: express-config
    configMapKey: REDIS_URL
healthCheck:
  liveness:
    path: /health/live
    initialDelaySeconds: 30
    periodSeconds: 10
  readiness:
    path: /health/ready
    initialDelaySeconds: 5
    periodSeconds: 5
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Generated Manifests

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: express-api
  namespace: production
  labels:
    app: express-api
    version: v2.1.0
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: express-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: express-api
        version: v2.1.0
        tier: backend
    spec:
      containers:
        - name: express-api
          image: myregistry/express-api:v2.1.0
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          env:
            - name: NODE_ENV
              value: production
            - name: PORT
              value: "3000"
            - name: LOG_LEVEL
              value: info
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: express-config
                  key: REDIS_URL
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          resources:
            requests:
              memory: 256Mi
              cpu: 250m
            limits:
              memory: 512Mi
              cpu: 1000m
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
      restartPolicy: Always
      terminationGracePeriodSeconds: 30
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: express-api
  namespace: production
  labels:
    app: express-api
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: metrics
      protocol: TCP
  selector:
    app: express-api
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: express-config
  namespace: production
  labels:
    app: express-api
data:
  REDIS_URL: "redis://redis-cluster:6379"
  CACHE_TTL: "3600"
  MAX_PAYLOAD_SIZE: "10mb"
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: express-api
  namespace: production
  labels:
    app: express-api
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: express-api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: express-api
                port:
                  name: http
```

## Deployment Commands

```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f configmap.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl rollout status deployment/express-api -n production
kubectl get pods -n production -l app=express-api

# Check logs
kubectl logs -n production -l app=express-api --tail=100
```
