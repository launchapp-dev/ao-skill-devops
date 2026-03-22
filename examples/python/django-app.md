# Django Application Example

A traditional Django web application with Celery workers for background task processing.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: django-app
namespace: production
replicas: 2
image: myregistry/django-app:v2.3.0
ports:
  - name: http
    containerPort: 8000
    servicePort: 80
env:
  - name: DJANGO_SETTINGS_MODULE
    value: config.settings.production
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: django-config
    configMapKey: REDIS_URL
  - name: SECRET_KEY
    secretRef: django-secrets
    secretKey: SECRET_KEY
  - name: ALLOWED_HOSTS
    configMapRef: django-config
    configMapKey: ALLOWED_HOSTS
  - name: AWS_ACCESS_KEY_ID
    secretRef: aws-credentials
    secretKey: access-key
  - name: AWS_SECRET_ACCESS_KEY
    secretRef: aws-credentials
    secretKey: secret-key
  - name: AWS_STORAGE_BUCKET_NAME
    configMapRef: django-config
    configMapKey: AWS_STORAGE_BUCKET_NAME
healthCheck:
  liveness:
    path: /health/
    initialDelaySeconds: 30
    periodSeconds: 30
  readiness:
    path: /ready/
    initialDelaySeconds: 10
    periodSeconds: 10
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1500m"
```

## Generated Manifests

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: production
  labels:
    app: django-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: django-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: django-app
    spec:
      containers:
        - name: django-app
          image: myregistry/django-app:v2.3.0
          ports:
            - name: http
              containerPort: 8000
          env:
            - name: DJANGO_SETTINGS_MODULE
              value: config.settings.production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: django-config
                  key: REDIS_URL
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: django-secrets
                  key: SECRET_KEY
            - name: ALLOWED_HOSTS
              valueFrom:
                configMapKeyRef:
                  name: django-config
                  key: ALLOWED_HOSTS
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
            - name: AWS_STORAGE_BUCKET_NAME
              valueFrom:
                configMapKeyRef:
                  name: django-config
                  key: AWS_STORAGE_BUCKET_NAME
          livenessProbe:
            httpGet:
              path: /health/
              port: http
            initialDelaySeconds: 30
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready/
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              memory: 512Mi
              cpu: 500m
            limits:
              memory: 1Gi
              cpu: 1500m
          command: ["gunicorn"]
          args:
            - config.wsgi:application
            - --bind=0.0.0.0:8000
            - --workers=4
            - --timeout=120
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: django-app
  namespace: production
  labels:
    app: django-app
spec:
  type: LoadBalancer
  ports:
    - name: http
      port: 80
      targetPort: http
  selector:
    app: django-app
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-config
  namespace: production
data:
  REDIS_URL: "redis://redis:6379/1"
  ALLOWED_HOSTS: "app.example.com,www.example.com"
  AWS_STORAGE_BUCKET_NAME: "my-django-media"
  MEDIA_URL: "/media/"
  STATIC_URL: "/static/"
  CACHE_URL: "redis://redis:6379/0"
```

### Celery Worker Deployment

```yaml
# celery-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-celery-worker
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: django-celery-worker
  template:
    metadata:
      labels:
        app: django-celery-worker
    spec:
      containers:
        - name: celery
          image: myregistry/django-app:v2.3.0
          command: ["celery"]
          args:
            - -A
            - config
            - worker
            - --loglevel=info
            - --concurrency=4
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: django-config
                  key: REDIS_URL
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: django-secrets
                  key: SECRET_KEY
          resources:
            requests:
              memory: 512Mi
              cpu: 300m
            limits:
              memory: 1Gi
              cpu: 1000m
```

## Django Health Check Implementation

```python
# health/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    return JsonResponse({"status": "ok"})

def readiness_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ready"})
    except Exception as e:
        return JsonResponse({"status": "not ready", "error": str(e)}, status=503)
```

## Celery Beat Scheduler

```yaml
# celery-beat-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-celery-beat
  namespace: production
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: celery-beat
          image: myregistry/django-app:v2.3.0
          command: ["celery"]
          args:
            - -A
            - config
            - beat
            - --loglevel=info
            - --schedule=/tmp/celerybeat-schedule
```
