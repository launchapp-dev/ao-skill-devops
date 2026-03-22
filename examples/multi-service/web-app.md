# Web Application Stack Example

A complete web application with frontend (React), backend API, and PostgreSQL database.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                       │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Ingress    │────▶│   Frontend   │     │   Backend    │    │
│  │   (nginx)    │     │   (React)    │     │   (Node.js)  │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                        │        │
│                                                ┌──────────────┐ │
│                                                │  PostgreSQL  │ │
│                                                │  (Stateful)  │ │
│                                                └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Input Specifications

### Frontend Deployment

```yaml
# frontend/input.yaml
manifest_type: deployment
name: web-frontend
namespace: production
replicas: 3
image: myregistry/web-frontend:v1.2.0
ports:
  - name: http
    containerPort: 80
    servicePort: 80
  - name: https
    containerPort: 443
    servicePort: 443
env:
  - name: REACT_APP_API_URL
    value: https://api.example.com
  - name: REACT_APP_ENVIRONMENT
    value: production
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "200m"
```

### Backend API Deployment

```yaml
# backend/input.yaml
manifest_type: deployment
name: web-backend
namespace: production
replicas: 3
image: myregistry/web-backend:v2.1.0
ports:
  - name: http
    containerPort: 3000
    servicePort: 80
env:
  - name: NODE_ENV
    value: production
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: backend-config
    configMapKey: REDIS_URL
  - name: JWT_SECRET
    secretRef: backend-secrets
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
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

### Database Deployment

```yaml
# database/input.yaml
manifest_type: deployment
name: postgres
namespace: production
replicas: 1
image: postgres:15-alpine
ports:
  - name: postgres
    containerPort: 5432
    servicePort: 5432
env:
  - name: POSTGRES_DB
    configMapRef: postgres-config
    configMapKey: POSTGRES_DB
  - name: POSTGRES_USER
    secretRef: postgres-credentials
    secretKey: POSTGRES_USER
  - name: POSTGRES_PASSWORD
    secretRef: postgres-credentials
    secretKey: POSTGRES_PASSWORD
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
volume:
  size: 20Gi
  storageClass: standard-ssd
  accessMode: ReadWriteOnce
```

## Generated Manifests

### Frontend Deployment

```yaml
# frontend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-frontend
  template:
    metadata:
      labels:
        app: web-frontend
    spec:
      containers:
        - name: web-frontend
          image: myregistry/web-frontend:v1.2.0
          ports:
            - name: http
              containerPort: 80
            - name: https
              containerPort: 443
          env:
            - name: REACT_APP_API_URL
              value: https://api.example.com
            - name: REACT_APP_ENVIRONMENT
              value: production
          resources:
            requests:
              memory: 64Mi
              cpu: 50m
            limits:
              memory: 128Mi
              cpu: 200m
```

### Backend Deployment

```yaml
# backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-backend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-backend
  template:
    metadata:
      labels:
        app: web-backend
    spec:
      containers:
        - name: web-backend
          image: myregistry/web-backend:v2.1.0
          ports:
            - name: http
              containerPort: 3000
          env:
            - name: NODE_ENV
              value: production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: backend-config
                  key: REDIS_URL
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: JWT_SECRET
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
              memory: 256Mi
              cpu: 250m
            limits:
              memory: 512Mi
              cpu: 1000m
```

### Database StatefulSet

```yaml
# database/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: production
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          ports:
            - name: postgres
              containerPort: 5432
          env:
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: postgres-config
                  key: POSTGRES_DB
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: POSTGRES_PASSWORD
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          resources:
            requests:
              memory: 512Mi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 2000m
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard-ssd
        resources:
          requests:
            storage: 20Gi
```

### Services

```yaml
# frontend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-frontend
  namespace: production
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: web-frontend

---
# backend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-backend
  namespace: production
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: web-backend

---
# database/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: production
spec:
  type: ClusterIP
  clusterIP: None  # Headless for StatefulSet
  ports:
    - name: postgres
      port: 5432
      targetPort: postgres
  selector:
    app: postgres
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-set-header: X-Forwarded-Proto https
spec:
  tls:
    - hosts:
        - example.com
        - www.example.com
        - api.example.com
      secretName: web-app-tls
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-frontend
                port:
                  name: http
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-backend
                port:
                  name: http
```
