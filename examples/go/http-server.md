# Go HTTP Server Example

A high-performance HTTP server built with Go, optimized for low memory usage and fast response times.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: go-http-server
namespace: production
replicas: 5
image: myregistry/go-http-server:v1.0.0
ports:
  - name: http
    containerPort: 8080
    servicePort: 80
  - name: pprof
    containerPort: 6060
    servicePort: 6060
env:
  - name: GOMAXPROCS
    value: "4"
  - name: GOMEMLIMIT
    value: "536870912"  # 512MiB
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: go-config
    configMapKey: REDIS_URL
  - name: LOG_LEVEL
    value: info
healthCheck:
  liveness:
    path: /healthz
    initialDelaySeconds: 5
    periodSeconds: 10
  readiness:
    path: /readyz
    initialDelaySeconds: 2
    periodSeconds: 5
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

## Generated Manifests

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-http-server
  namespace: production
  labels:
    app: go-http-server
    version: v1.0.0
spec:
  replicas: 5
  selector:
    matchLabels:
      app: go-http-server
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: go-http-server
        version: v1.0.0
    spec:
      containers:
        - name: go-http-server
          image: myregistry/go-http-server:v1.0.0
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: pprof
              containerPort: 6060
              protocol: TCP
          env:
            - name: GOMAXPROCS
              value: "4"
            - name: GOMEMLIMIT
              value: "536870912"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: go-config
                  key: REDIS_URL
            - name: LOG_LEVEL
              value: info
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 2
            periodSeconds: 5
          resources:
            requests:
              memory: 128Mi
              cpu: 100m
            limits:
              memory: 256Mi
              cpu: 500m
          securityContext:
            readOnlyRootFilesystem: true
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
  name: go-http-server
  namespace: production
  labels:
    app: go-http-server
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: pprof
      port: 6060
      targetPort: pprof
  selector:
    app: go-http-server
```

### HorizontalPodAutoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: go-http-server
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: go-http-server
  minReplicas: 2
  maxReplicas: 20
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
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: go-http-server
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: go-http-server
                port:
                  name: http
```

## Go Server Implementation

### Health Check Endpoints

```go
package main

import (
    "net/http"
    "database/sql"
)

var db *sql.DB

func healthz(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ok"}`))
}

func readyz(w http.ResponseWriter, r *http.Request) {
    if err := db.Ping(); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        w.Write([]byte(`{"status":"not ready","error":"database unavailable"}`))
        return
    }
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ready"}`))
}
```

### Graceful Shutdown

```go
func main() {
    srv := &http.Server{Addr: ":8080"}
    
    // Start server in goroutine
    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()
    
    // Wait for interrupt signal
    <-make(chan os.Signal, 1)
    
    // Graceful shutdown with timeout
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    srv.Shutdown(ctx)
}
```
