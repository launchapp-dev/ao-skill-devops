# Go gRPC Service Example

A production-ready gRPC microservice with streaming support, load balancing, and health checks.

## Input Specification

```yaml
# input.yaml
manifest_type: deployment
name: grpc-service
namespace: production
replicas: 3
image: myregistry/grpc-service:v1.0.0
ports:
  - name: grpc
    containerPort: 50051
    servicePort: 50051
  - name: grpc-web
    containerPort: 8080
    servicePort: 8080
  - name: metrics
    containerPort: 9090
    servicePort: 9090
env:
  - name: GRPC_PORT
    value: "50051"
  - name: DATABASE_URL
    secretRef: postgres-credentials
    secretKey: DATABASE_URL
  - name: REDIS_URL
    configMapRef: grpc-config
    configMapKey: REDIS_URL
  - name: JAEGER_ENDPOINT
    configMapRef: grpc-config
    configMapKey: JAEGER_ENDPOINT
  - name: LOG_LEVEL
    value: info
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
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
  name: grpc-service
  namespace: production
  labels:
    app: grpc-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: grpc-service
  template:
    metadata:
      labels:
        app: grpc-service
    spec:
      containers:
        - name: grpc-service
          image: myregistry/grpc-service:v1.0.0
          ports:
            - name: grpc
              containerPort: 50051
              protocol: TCP
            - name: grpc-web
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          env:
            - name: GRPC_PORT
              value: "50051"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: grpc-config
                  key: REDIS_URL
            - name: JAEGER_ENDPOINT
              valueFrom:
                configMapKeyRef:
                  name: grpc-config
                  key: JAEGER_ENDPOINT
            - name: LOG_LEVEL
              value: info
          resources:
            requests:
              memory: 256Mi
              cpu: 200m
            limits:
              memory: 512Mi
              cpu: 1000m
          securityContext:
            readOnlyRootFilesystem: true
          ports:
            - containerPort: 50051
              name: grpc
          readinessProbe:
            exec:
              command:
                - /bin/grpc_health_probe
                - -addr=:50051
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            exec:
              command:
                - /bin/grpc_health_probe
                - -addr=:50051
                - -service=grpc.health.v1.Health
            initialDelaySeconds: 10
            periodSeconds: 20
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: grpc-service
  namespace: production
  labels:
    app: grpc-service
  annotations:
    cloud.google.com/backend-config: '{"default": "grpc-service-backend"}'
spec:
  type: ClusterIP
  ports:
    - name: grpc
      port: 50051
      targetPort: grpc
      protocol: TCP
    - name: grpc-web
      port: 8080
      targetPort: grpc-web
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: metrics
      protocol: TCP
  selector:
    app: grpc-service
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grpc-config
  namespace: production
data:
  REDIS_URL: "redis://redis:6379/2"
  JAEGER_ENDPOINT: "http://jaeger-collector:14268/api/traces"
  GRPC_MAX_MESSAGE_SIZE: "8388608"  # 8MB
  GRPC_KEEPALIVE_TIME: "120s"
```

## gRPC Service Implementation

### Proto Definition

```protobuf
syntax = "proto3";

package myservice.v1;

service MyService {
  rpc GetItem(GetItemRequest) returns (GetItemResponse);
  rpc StreamItems(StreamItemsRequest) returns (stream Item);
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}

message GetItemRequest {
  string id = 1;
}

message GetItemResponse {
  Item item = 1;
}

message Item {
  string id = 1;
  string name = 2;
  int64 created_at = 3;
}

message StreamItemsRequest {
  repeated string ids = 1;
}

message HealthCheckRequest {}

message HealthCheckResponse {
  string status = 1;
}
```

### Health Check Implementation

```go
package main

import (
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

var healthServer = health.NewServer()

func init() {
    healthpb.RegisterHealthServer(grpcServer, &HealthService{})
}

type HealthService struct {
    healthpb.UnimplementedHealthServer
}

func (s *HealthService) Check(ctx context.Context, req *healthpb.HealthCheckRequest) (*healthpb.HealthCheckResponse, error) {
    return &healthpb.HealthCheckResponse{
        Status: healthpb.HealthCheckResponse_SERVING,
    }, nil
}
```

## gRPC Ingress (Ambassador/Gloo)

For gRPC ingress routing, use an appropriate ingress controller:

```yaml
# Values for gloo or ambassador
apiVersion: gloo.solo.io/v1
kind: VirtualService
metadata:
  name: grpc-service
spec:
  virtualHost:
    domains:
      - grpc.example.com
    routes:
      - matchers:
          - prefix: /
        options:
          upstreamSpec:
            grpc:
              - serviceName: grpc-service
                serviceNamespace: production
```
