"""
Test fixtures and utilities for ao-skill-devops skill pack.

This module provides shared fixtures for testing all DevOps generator skills:
- Dockerfile Generator
- GitHub Actions Generator
- Kubernetes Manifest Generator
- Docker Compose Generator
- Vercel Config Generator
- Railway Config Generator
- Integration Tester
"""

import os
import json
import tempfile
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Generator
from unittest.mock import MagicMock, patch, AsyncMock
import yaml


# =============================================================================
# Mock File System Fixtures
# =============================================================================

class MockFileSystem:
    """In-memory mock file system for testing without actual I/O."""
    
    def __init__(self):
        self.files: Dict[str, str] = {}
        self.directories: set = {"/"}
    
    def write(self, path: str, content: str) -> None:
        """Write content to a file path."""
        self.files[path] = content
        # Ensure parent directories exist
        parts = Path(path).parts[:-1]
        for i in range(len(parts)):
            dir_path = str(Path(*parts[:i+1]))
            if not dir_path.startswith("/"):
                dir_path = "/" + dir_path
            self.directories.add(dir_path)
    
    def read(self, path: str) -> str:
        """Read content from a file path."""
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path]
    
    def exists(self, path: str) -> bool:
        """Check if a file or directory exists."""
        return path in self.files or path in self.directories
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        return path in self.files
    
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        return path in self.directories
    
    def list_dir(self, path: str) -> List[str]:
        """List contents of a directory."""
        if path not in self.directories:
            raise NotADirectoryError(f"Not a directory: {path}")
        results = set()
        prefix = path if path == "/" else path.rstrip("/") + "/"
        # Add files in this directory
        for f in self.files:
            if f == path:
                continue
            if f.startswith(prefix):
                rel = f[len(prefix):]
                if "/" not in rel:
                    results.add(rel)
        # Add subdirectories
        for d in self.directories:
            if d == path:
                continue
            if d.startswith(prefix):
                rel = d[len(prefix):]
                if "/" in rel:
                    results.add(rel.split("/")[0])
                elif rel:
                    results.add(rel)
        return sorted(results)
    
    def remove(self, path: str) -> None:
        """Remove a file."""
        if path in self.files:
            del self.files[path]
    
    def makedirs(self, path: str) -> None:
        """Create a directory and all parents."""
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        self.directories.add(path)
        # Add all parent directories
        parts = path.strip("/").split("/")
        for i in range(len(parts)):
            parent = "/" + "/".join(parts[:i+1])
            self.directories.add(parent)
    
    def get_tree(self) -> Dict[str, Any]:
        """Get the full file system tree as a nested dict."""
        result = {}
        for path, content in self.files.items():
            parts = Path(path).parts
            current = result
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = content
        return result


class TempProjectDir:
    """Context manager for creating temporary project directories."""
    
    def __init__(self, structure: Optional[Dict[str, Any]] = None):
        self.structure = structure or {}
        self.temp_dir = None
        self.original_cwd = None
    
    def __enter__(self) -> Path:
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        self._create_structure(self.temp_dir, self.structure)
        return self.temp_dir
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_cwd)
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_structure(self, base: Path, structure: Dict[str, Any]) -> None:
        """Recursively create directory structure."""
        for name, content in structure.items():
            path = base / name
            if isinstance(content, dict):
                path.mkdir(exist_ok=True)
                self._create_structure(path, content)
            else:
                path.parent.mkdir(exist_ok=True)
                path.write_text(str(content))


@contextmanager
def mock_file_system_ctx(initial: Optional[Dict[str, str]] = None) -> Generator[MockFileSystem, None, None]:
    """Context manager for MockFileSystem with optional initial files."""
    fs = MockFileSystem()
    if initial:
        for path, content in initial.items():
            fs.write(path, content)
    yield fs


# =============================================================================
# Sample Inputs for Each Generator Type
# =============================================================================

# -----------------------------------------------------------------------------
# Dockerfile Generator Inputs
# -----------------------------------------------------------------------------

DOCKERFILE_NODEJS_MULTISTAGE = {
    "build_type": "multistage",
    "language": "nodejs",
    "language_version": "20.x",
    "build_command": "npm run build",
    "start_command": "npm start",
    "port": 3000,
    "healthcheck": {
        "cmd": "curl -f http://localhost:3000/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3,
        "start_period": "40s"
    },
    "environment_variables": {
        "NODE_ENV": "production"
    },
    "user": "node"
}

DOCKERFILE_PYTHON_MULTISTAGE = {
    "build_type": "multistage",
    "language": "python",
    "language_version": "3.12",
    "build_command": "pip install -r requirements.txt",
    "start_command": "gunicorn app:app --bind 0.0.0.0:8000",
    "port": 8000,
    "healthcheck": {
        "cmd": "curl -f http://localhost:8000/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3
    },
    "environment_variables": {
        "FLASK_ENV": "production"
    },
    "user": "app"
}

DOCKERFILE_GO_MULTISTAGE = {
    "build_type": "multistage",
    "language": "go",
    "language_version": "1.21",
    "build_command": "go build -o main ./cmd/server",
    "start_command": "./main",
    "port": 8080,
    "healthcheck": {
        "cmd": "wget -qO- http://localhost:8080/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3
    },
    "user": "app"
}

DOCKERFILE_RUST_MULTISTAGE = {
    "build_type": "multistage",
    "language": "rust",
    "language_version": "1.70",
    "build_command": "cargo build --release",
    "start_command": "/app/server",
    "port": 8080,
    "environment_variables": {
        "RUST_LOG": "info"
    },
    "healthcheck": {
        "cmd": "curl -f http://localhost:8080/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3
    }
}

DOCKERFILE_STATIC_SITE = {
    "build_type": "multistage",
    "language": "static",
    "build_command": "npm run build",
    "output_directory": "dist",
    "port": 80,
    "healthcheck": {
        "cmd": "wget -qO- http://localhost/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3
    },
    "user": "nginx"
}

DOCKERFILE_DISTROLESS = {
    "build_type": "distroless",
    "language": "nodejs",
    "language_version": "20",
    "build_command": "npm run build",
    "start_command": "npm start",
    "port": 3000,
    "builder_image": "node:20-alpine",
    "final_image": "gcr.io/distroless/nodejs20-debian11",
    "healthcheck": {
        "cmd": "curl -f http://localhost:3000/health || exit 1",
        "interval": "30s",
        "timeout": "5s",
        "retries": 3
    },
    "environment_variables": {
        "NODE_ENV": "production"
    },
    "user": "nonroot"
}

DOCKERFILE_SCRATCH = {
    "build_type": "scratch",
    "language": "go",
    "language_version": "1.21",
    "build_command": "go build -ldflags '-w -s' -o /bin/app ./cmd",
    "start_command": "/bin/app",
    "port": 8080
}

DOCKERFILE_GENERATOR_INPUTS = {
    "nodejs_multistage": DOCKERFILE_NODEJS_MULTISTAGE,
    "python_multistage": DOCKERFILE_PYTHON_MULTISTAGE,
    "go_multistage": DOCKERFILE_GO_MULTISTAGE,
    "rust_multistage": DOCKERFILE_RUST_MULTISTAGE,
    "static_site": DOCKERFILE_STATIC_SITE,
    "distroless": DOCKERFILE_DISTROLESS,
    "scratch": DOCKERFILE_SCRATCH,
}


# -----------------------------------------------------------------------------
# GitHub Actions Generator Inputs
# -----------------------------------------------------------------------------

GITHUB_ACTIONS_NODEJS_CI = {
    "environment": "nodejs",
    "workflow_type": "ci",
    "name": "Node.js CI",
    "language_version": "20.x",
    "steps": ["lint", "test", "build"],
    "cache": True,
    "matrix": {
        "os": ["ubuntu-latest", "macos-latest"],
        "node-version": ["18.x", "20.x"]
    }
}

GITHUB_ACTIONS_PYTHON_CICD = {
    "environment": "python",
    "workflow_type": "ci-cd",
    "name": "Python CI/CD",
    "language_version": "3.11",
    "steps": ["lint", "test", "build", "docker", "deploy"],
    "cache": True,
    "docker": {
        "image_name": "myregistry/myapp",
        "dockerfile": "./Dockerfile"
    }
}

GITHUB_ACTIONS_GO_CD = {
    "environment": "go",
    "workflow_type": "cd",
    "name": "Go CD Pipeline",
    "language_version": "1.21",
    "steps": ["test", "build", "docker"],
    "cache": True,
    "artifact": {
        "name": "binary",
        "path": "./dist"
    }
}

GITHUB_ACTIONS_NODEJS_MATRIX = {
    "environment": "nodejs",
    "workflow_type": "ci",
    "name": "Node.js Matrix CI",
    "language_version": "20.x",
    "steps": ["lint", "test", "build"],
    "cache": True,
    "matrix": {
        "os": ["ubuntu-latest", "windows-latest"],
        "node-version": ["16.x", "18.x", "20.x"]
    }
}

GITHUB_ACTIONS_GENERATOR_INPUTS = {
    "nodejs_ci": GITHUB_ACTIONS_NODEJS_CI,
    "python_cicd": GITHUB_ACTIONS_PYTHON_CICD,
    "go_cd": GITHUB_ACTIONS_GO_CD,
    "nodejs_matrix": GITHUB_ACTIONS_NODEJS_MATRIX,
}


# -----------------------------------------------------------------------------
# Kubernetes Manifest Generator Inputs
# -----------------------------------------------------------------------------

K8S_DEPLOYMENT = {
    "manifest_type": "deployment",
    "name": "my-app",
    "namespace": "production",
    "spec": {
        "replicas": 3,
        "image": "myregistry/myapp:v1.2.3",
        "ports": [
            {"name": "http", "containerPort": 8080, "servicePort": 80}
        ]
    }
}

K8S_SERVICE = {
    "manifest_type": "service",
    "name": "my-app-service",
    "namespace": "production",
    "spec": {
        "type": "ClusterIP",
        "selector": {"app": "my-app"},
        "ports": [
            {"name": "http", "port": 80, "targetPort": 8080}
        ]
    }
}

K8S_INGRESS = {
    "manifest_type": "ingress",
    "name": "my-app-ingress",
    "namespace": "production",
    "spec": {
        "ingressClassName": "nginx",
        "rules": [
            {
                "host": "myapp.example.com",
                "paths": [
                    {"path": "/", "pathType": "Prefix", "service": "my-app-service", "servicePort": 80}
                ]
            }
        ]
    }
}

K8S_CONFIGMAP = {
    "manifest_type": "configmap",
    "name": "app-config",
    "namespace": "production",
    "data": {
        "DATABASE_URL": "postgres://db:5432/myapp",
        "REDIS_URL": "redis://redis:6379",
        "LOG_LEVEL": "info"
    }
}

K8S_SECRET = {
    "manifest_type": "secret",
    "name": "app-secrets",
    "namespace": "production",
    "type": "Opaque",
    "stringData": {
        "DATABASE_PASSWORD": "secretpassword",
        "API_KEY": "apikey12345"
    }
}

K8S_PVC = {
    "manifest_type": "pvc",
    "name": "data-pvc",
    "namespace": "production",
    "spec": {
        "accessModes": ["ReadWriteOnce"],
        "resources": {"requests": {"storage": "10Gi"}},
        "storageClassName": "standard"
    }
}

K8S_HELM = {
    "manifest_type": "helm",
    "chart_name": "my-chart",
    "namespace": "production",
    "values": {
        "replicaCount": 2,
        "image": {
            "repository": "myapp",
            "tag": "latest"
        },
        "service": {
            "type": "ClusterIP",
            "port": 80
        }
    }
}

K8S_KUSTOMIZE = {
    "manifest_type": "kustomize",
    "base_chart": "./base",
    "overlays": [
        {"name": "dev", "replicas": 1, "image_tag": "dev"},
        {"name": "prod", "replicas": 5, "image_tag": "stable"}
    ]
}

K8S_MANIFEST_GENERATOR_INPUTS = {
    "deployment": K8S_DEPLOYMENT,
    "service": K8S_SERVICE,
    "ingress": K8S_INGRESS,
    "configmap": K8S_CONFIGMAP,
    "secret": K8S_SECRET,
    "pvc": K8S_PVC,
    "helm": K8S_HELM,
    "kustomize": K8S_KUSTOMIZE,
}


# -----------------------------------------------------------------------------
# Docker Compose Generator Inputs
# -----------------------------------------------------------------------------

DOCKER_COMPOSE_BASIC = {
    "compose_version": "3.8",
    "services": [
        {
            "name": "web",
            "image": "nginx:alpine",
            "ports": ["80:80"],
            "volumes": ["./html:/usr/share/nginx/html:ro"],
            "healthcheck": {
                "test": "curl -f http://localhost/ || exit 1",
                "interval": "30s",
                "timeout": "5s",
                "retries": 3
            },
            "restart": "unless-stopped"
        }
    ]
}

DOCKER_COMPOSE_WITH_DB = {
    "compose_version": "3.8",
    "services": [
        {
            "name": "api",
            "build": {"context": ".", "dockerfile": "Dockerfile"},
            "ports": ["3000:3000"],
            "environment": {
                "DATABASE_URL": "postgres://postgres:secret@db:5432/myapp",
                "NODE_ENV": "production"
            },
            "depends_on": ["db", "redis"],
            "healthcheck": {
                "test": "curl -f http://localhost:3000/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s"
            },
            "restart": "unless-stopped"
        },
        {
            "name": "db",
            "image": "postgres:15-alpine",
            "environment": {
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "secret",
                "POSTGRES_DB": "myapp"
            },
            "volumes": ["db_data:/var/lib/postgresql/data"],
            "healthcheck": {
                "test": ["CMD", "pg_isready", "-U", "postgres"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5
            }
        },
        {
            "name": "redis",
            "image": "redis:7-alpine",
            "volumes": ["redis_data:/data"],
            "healthcheck": {
                "test": ["CMD", "redis-cli", "ping"],
                "interval": "10s",
                "timeout": "5s",
                "retries": 5
            }
        }
    ],
    "networks": [
        {"name": "backend", "driver": "bridge"}
    ],
    "volumes": [
        {"name": "db_data", "driver": "local"},
        {"name": "redis_data", "driver": "local"}
    ]
}

DOCKER_COMPOSE_DEV_STACK = {
    "compose_version": "3.8",
    "services": [
        {
            "name": "app",
            "build": {"context": ".", "dockerfile": "Dockerfile.dev"},
            "ports": ["3000:3000", "9229:9229"],
            "environment": {
                "NODE_ENV": "development",
                "DEBUG": "true"
            },
            "volumes": [".:/app", "/app/node_modules"],
            "tty": True,
            "stdin_open": True,
            "depends_on": ["db", "redis"]
        },
        {
            "name": "db",
            "image": "postgres:15-alpine",
            "environment": {
                "POSTGRES_USER": "dev",
                "POSTGRES_PASSWORD": "dev",
                "POSTGRES_DB": "devdb"
            },
            "ports": ["5432:5432"],
            "volumes": ["pg_data:/var/lib/postgresql/data"]
        },
        {
            "name": "redis",
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
            "volumes": ["redis_data:/data"]
        }
    ],
    "networks": [{"name": "dev", "driver": "bridge"}],
    "volumes": [
        {"name": "pg_data", "driver": "local"},
        {"name": "redis_data", "driver": "local"}
    ]
}

DOCKER_COMPOSE_WITH_SECRETS = {
    "compose_version": "3.8",
    "services": [
        {
            "name": "api",
            "image": "myregistry/myapp:v1.0.0",
            "ports": ["8080:8080"],
            "secrets": ["db_password", "api_key"],
            "environment": {"NODE_ENV": "production", "DATABASE_HOST": "db"},
            "depends_on": {"db": {"condition": "service_healthy"}, "redis": {"condition": "service_started"}},
            "healthcheck": {
                "test": "curl -f http://localhost:8080/health || exit 1",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "30s"
            },
            "restart": "unless-stopped",
            "logging": {"driver": "json-file", "options": {"max-size": "100m", "max-file": "3"}}
        }
    ],
    "networks": [{"name": "production", "driver": "bridge"}],
    "secrets": [
        {"name": "db_password", "file": "./secrets/db_password.txt"},
        {"name": "api_key", "file": "./secrets/api_key.txt"}
    ]
}

DOCKER_COMPOSE_GENERATOR_INPUTS = {
    "basic": DOCKER_COMPOSE_BASIC,
    "with_db": DOCKER_COMPOSE_WITH_DB,
    "dev_stack": DOCKER_COMPOSE_DEV_STACK,
    "with_secrets": DOCKER_COMPOSE_WITH_SECRETS,
}


# -----------------------------------------------------------------------------
# Vercel Config Generator Inputs
# -----------------------------------------------------------------------------

VERCEL_STATIC_SITE = {
    "deployment_type": "static",
    "build_command": "npm run build",
    "output_directory": "dist",
    "environment_variables": {"NODE_ENV": "production"}
}

VERCEL_SERVERLESS_API = {
    "deployment_type": "serverless",
    "framework": "nodejs",
    "build_command": "npm run build",
    "functions": {
        "api": {"runtime": "nodejs18.x", "memory": 1024, "maxDuration": 10}
    },
    "environment_variables": {"DATABASE_URL": "${{ secrets.DATABASE_URL }}"}
}

VERCEL_NEXTJS = {
    "deployment_type": "framework",
    "framework": "nextjs",
    "regions": ["iad1", "sfo1"],
    "routes": [
        {"src": "/api/(.*)", "dest": "/api/$1"},
        {"src": "/(.*)", "dest": "/$1", "headers": [{"x-custom-header": "value"}]}
    ]
}

VERCEL_MONOREPO = {
    "deployment_type": "monorepo",
    "regions": ["iad1"],
    "functions": {"api": {"memory": 512, "maxDuration": 30}},
    "environment_variables": {"NODE_ENV": "production"}
}

VERCEL_EDGE_FUNCTION = {
    "deployment_type": "edge",
    "framework": "nodejs",
    "regions": ["iad1", "sfo1", "hnd1"],
    "functions": {
        "edge-handler": {"runtime": "edge-nodejs18.x"}
    }
}

VERCEL_CONFIG_GENERATOR_INPUTS = {
    "static_site": VERCEL_STATIC_SITE,
    "serverless_api": VERCEL_SERVERLESS_API,
    "nextjs": VERCEL_NEXTJS,
    "monorepo": VERCEL_MONOREPO,
    "edge_function": VERCEL_EDGE_FUNCTION,
}


# -----------------------------------------------------------------------------
# Railway Config Generator Inputs
# -----------------------------------------------------------------------------

RAILWAY_DOCKER = {
    "deployment_type": "docker",
    "dockerfile_path": "Dockerfile",
    "docker_context": ".",
    "port": 8080,
    "num_replicas": 2,
    "healthcheck_path": "/health",
    "environment_variables": {"NODE_ENV": "production", "PORT": "8080"},
    "secret_variables": ["DATABASE_URL", "API_KEY"],
    "memory_limit": 512,
    "cpu": 1
}

RAILWAY_NIXPACKS_NODE = {
    "deployment_type": "nixpacks",
    "language": "nodejs",
    "build_command": "npm run build",
    "start_command": "npm start",
    "port": 3000,
    "healthcheck_path": "/health",
    "environment_variables": {"NODE_ENV": "production"},
    "secret_variables": ["DATABASE_URL"]
}

RAILWAY_NIXPACKS_PYTHON = {
    "deployment_type": "nixpacks",
    "language": "python",
    "build_command": "pip install -r requirements.txt",
    "start_command": "gunicorn app:app",
    "port": 8000,
    "healthcheck_path": "/health",
    "healthcheck_retries": 5,
    "environment_variables": {"FLASK_ENV": "production"},
    "secret_variables": ["SECRET_KEY", "DATABASE_URL"]
}

RAILWAY_MONOREPO = {
    "deployment_type": "monorepo",
    "services": [
        {
            "name": "api",
            "path": "./services/api",
            "deployment_type": "docker",
            "dockerfile_path": "./services/api/Dockerfile",
            "port": 4000,
            "healthcheck_path": "/health"
        },
        {
            "name": "worker",
            "path": "./services/worker",
            "deployment_type": "nixpacks",
            "language": "nodejs",
            "port": 4001
        },
        {
            "name": "web",
            "path": "./apps/web",
            "deployment_type": "nixpacks",
            "language": "nodejs",
            "port": 3000,
            "healthcheck_path": "/"
        }
    ]
}

RAILWAY_STATIC = {
    "deployment_type": "static",
    "build_command": "npm run build",
    "output_directory": "dist",
    "environment_variables": {"NODE_ENV": "production"}
}

RAILWAY_CONFIG_GENERATOR_INPUTS = {
    "docker": RAILWAY_DOCKER,
    "nixpacks_node": RAILWAY_NIXPACKS_NODE,
    "nixpacks_python": RAILWAY_NIXPACKS_PYTHON,
    "monorepo": RAILWAY_MONOREPO,
    "static": RAILWAY_STATIC,
}


# -----------------------------------------------------------------------------
# Integration Tester Inputs
# -----------------------------------------------------------------------------

INTEGRATION_TEST_CONFIG = {
    "test_type": "config",
    "target_config": "./output/deployment.yaml",
    "validation_level": "strict"
}

INTEGRATION_TEST_E2E = {
    "test_type": "e2e",
    "target_config": "./output/ci.yaml",
    "test_scenario": "pr_opened",
    "mock_mode": True
}

INTEGRATION_TEST_CLI = {
    "test_type": "cli",
    "target_config": "./output/Dockerfile",
    "test_scenario": "build_and_run",
    "mock_mode": False
}

INTEGRATION_TESTER_INPUTS = {
    "config_validation": INTEGRATION_TEST_CONFIG,
    "e2e_test": INTEGRATION_TEST_E2E,
    "cli_test": INTEGRATION_TEST_CLI,
}


# -----------------------------------------------------------------------------
# All Generator Inputs Combined
# -----------------------------------------------------------------------------

ALL_GENERATOR_INPUTS = {
    "dockerfile": DOCKERFILE_GENERATOR_INPUTS,
    "github_actions": GITHUB_ACTIONS_GENERATOR_INPUTS,
    "k8s_manifest": K8S_MANIFEST_GENERATOR_INPUTS,
    "docker_compose": DOCKER_COMPOSE_GENERATOR_INPUTS,
    "vercel_config": VERCEL_CONFIG_GENERATOR_INPUTS,
    "railway_config": RAILWAY_CONFIG_GENERATOR_INPUTS,
    "integration_tester": INTEGRATION_TESTER_INPUTS,
}


# =============================================================================
# Pytest Fixtures
# =============================================================================

import pytest


@pytest.fixture
def mock_fs() -> Generator[MockFileSystem, None, None]:
    """Provide a fresh MockFileSystem instance for each test."""
    yield MockFileSystem()


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Provide a temporary project directory with optional structure."""
    with TempProjectDir() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_project_structure() -> Dict[str, Any]:
    """Provide a sample project structure for testing."""
    return {
        "package.json": json.dumps({
            "name": "test-project",
            "version": "1.0.0",
            "scripts": {"build": "tsc", "test": "jest"}
        }),
        "src": {
            "index.ts": "console.log('Hello World');",
            "app.ts": "export const app = {};"
        },
        "Dockerfile": "FROM node:20\nCMD [\"node\", \"index.js\"]"
    }


@pytest.fixture
def temp_project_with_structure(sample_project_structure: Dict[str, Any]) -> Generator[Path, None, None]:
    """Provide a temporary project directory with sample structure."""
    with TempProjectDir(sample_project_structure) as temp_dir:
        yield temp_dir


# -----------------------------------------------------------------------------
# Dockerfile Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(DOCKERFILE_GENERATOR_INPUTS.keys()))
def dockerfile_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all Dockerfile generator inputs."""
    return DOCKERFILE_GENERATOR_INPUTS[request.param]


@pytest.fixture
def dockerfile_nodejs_input() -> Dict[str, Any]:
    """Provide Node.js Dockerfile input."""
    return DOCKERFILE_NODEJS_MULTISTAGE.copy()


@pytest.fixture
def dockerfile_python_input() -> Dict[str, Any]:
    """Provide Python Dockerfile input."""
    return DOCKERFILE_PYTHON_MULTISTAGE.copy()


@pytest.fixture
def dockerfile_go_input() -> Dict[str, Any]:
    """Provide Go Dockerfile input."""
    return DOCKERFILE_GO_MULTISTAGE.copy()


# -----------------------------------------------------------------------------
# GitHub Actions Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(GITHUB_ACTIONS_GENERATOR_INPUTS.keys()))
def github_actions_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all GitHub Actions generator inputs."""
    return GITHUB_ACTIONS_GENERATOR_INPUTS[request.param]


@pytest.fixture
def github_actions_nodejs_input() -> Dict[str, Any]:
    """Provide Node.js GitHub Actions input."""
    return GITHUB_ACTIONS_NODEJS_CI.copy()


@pytest.fixture
def github_actions_python_input() -> Dict[str, Any]:
    """Provide Python GitHub Actions input."""
    return GITHUB_ACTIONS_PYTHON_CICD.copy()


# -----------------------------------------------------------------------------
# Kubernetes Manifest Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(K8S_MANIFEST_GENERATOR_INPUTS.keys()))
def k8s_manifest_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all K8s manifest generator inputs."""
    return K8S_MANIFEST_GENERATOR_INPUTS[request.param]


@pytest.fixture
def k8s_deployment_input() -> Dict[str, Any]:
    """Provide Kubernetes Deployment input."""
    return K8S_DEPLOYMENT.copy()


@pytest.fixture
def k8s_service_input() -> Dict[str, Any]:
    """Provide Kubernetes Service input."""
    return K8S_SERVICE.copy()


@pytest.fixture
def k8s_ingress_input() -> Dict[str, Any]:
    """Provide Kubernetes Ingress input."""
    return K8S_INGRESS.copy()


# -----------------------------------------------------------------------------
# Docker Compose Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(DOCKER_COMPOSE_GENERATOR_INPUTS.keys()))
def docker_compose_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all Docker Compose generator inputs."""
    return DOCKER_COMPOSE_GENERATOR_INPUTS[request.param]


@pytest.fixture
def docker_compose_basic_input() -> Dict[str, Any]:
    """Provide basic Docker Compose input."""
    return DOCKER_COMPOSE_BASIC.copy()


@pytest.fixture
def docker_compose_with_db_input() -> Dict[str, Any]:
    """Provide Docker Compose input with database."""
    return DOCKER_COMPOSE_WITH_DB.copy()


# -----------------------------------------------------------------------------
# Vercel Config Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(VERCEL_CONFIG_GENERATOR_INPUTS.keys()))
def vercel_config_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all Vercel config generator inputs."""
    return VERCEL_CONFIG_GENERATOR_INPUTS[request.param]


@pytest.fixture
def vercel_static_input() -> Dict[str, Any]:
    """Provide Vercel static site input."""
    return VERCEL_STATIC_SITE.copy()


@pytest.fixture
def vercel_nextjs_input() -> Dict[str, Any]:
    """Provide Vercel Next.js input."""
    return VERCEL_NEXTJS.copy()


# -----------------------------------------------------------------------------
# Railway Config Generator Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(RAILWAY_CONFIG_GENERATOR_INPUTS.keys()))
def railway_config_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all Railway config generator inputs."""
    return RAILWAY_CONFIG_GENERATOR_INPUTS[request.param]


@pytest.fixture
def railway_docker_input() -> Dict[str, Any]:
    """Provide Railway Docker deployment input."""
    return RAILWAY_DOCKER.copy()


@pytest.fixture
def railway_nixpacks_input() -> Dict[str, Any]:
    """Provide Railway Nixpacks deployment input."""
    return RAILWAY_NIXPACKS_NODE.copy()


# -----------------------------------------------------------------------------
# Integration Tester Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture(params=list(INTEGRATION_TESTER_INPUTS.keys()))
def integration_test_input(request) -> Dict[str, Any]:
    """Parametrized fixture providing all integration test inputs."""
    return INTEGRATION_TESTER_INPUTS[request.param]


# =============================================================================
# Test Utilities
# =============================================================================

def validate_yaml_syntax(content: str) -> bool:
    """Validate YAML syntax without strict schema checking."""
    try:
        yaml.safe_load(content)
        return True
    except yaml.YAMLError:
        return False


def validate_json_syntax(content: str) -> bool:
    """Validate JSON syntax."""
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False


def validate_dockerfile_syntax(content: str) -> bool:
    """Basic validation of Dockerfile syntax."""
    valid_instructions = {
        "FROM", "RUN", "CMD", "LABEL", "EXPOSE", "ENV", "ADD", "COPY",
        "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD",
        "STOPSIGNAL", "HEALTHCHECK", "SHELL", "MAINTAINER"
    }
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        instruction = line.split()[0].upper()
        if instruction not in valid_instructions:
            return False
    return True


def validate_github_actions_workflow(content: str) -> bool:
    """Validate GitHub Actions workflow YAML structure."""
    if not validate_yaml_syntax(content):
        return False
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return False
        # Check for required top-level keys
        if "on" not in data and "name" not in data:
            return False
        return True
    except Exception:
        return False


def validate_kubernetes_manifest(content: str) -> bool:
    """Validate Kubernetes manifest structure."""
    if not validate_yaml_syntax(content):
        return False
    try:
        data = yaml.safe_load(content)
        if isinstance(data, list):
            docs = data
        else:
            docs = [data]
        for doc in docs:
            if not isinstance(doc, dict):
                return False
            # Check for required K8s resource fields
            if "apiVersion" not in doc or "kind" not in doc:
                return False
        return True
    except Exception:
        return False


def validate_docker_compose(content: str) -> bool:
    """Validate Docker Compose file structure."""
    if not validate_yaml_syntax(content):
        return False
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return False
        if "version" not in data and "services" not in data:
            return False
        return True
    except Exception:
        return False


def validate_vercel_config(content: str) -> bool:
    """Validate Vercel configuration JSON."""
    if not validate_json_syntax(content):
        return False
    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            return False
        return True
    except Exception:
        return False


def validate_railway_config(content: str) -> bool:
    """Validate Railway configuration TOML-like structure."""
    # Basic validation - checks for expected sections
    required_sections = ["deployment"]
    for section in required_sections:
        if section not in content:
            return False
    return True


class MockGitHubAPI:
    """Mock GitHub API for testing."""
    
    def __init__(self, token: str = "test-token"):
        self.token = token
        self.workflows = {}
        self.actions = {}
    
    def create_workflow(self, repo: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Mock create workflow API call."""
        return {"id": "wf_123", "name": workflow.get("name", "Test")}
    
    def get_workflow_runs(self, repo: str, workflow_id: str) -> List[Dict[str, Any]]:
        """Mock get workflow runs API call."""
        return []


class MockDockerRegistry:
    """Mock Docker Registry for testing."""
    
    def __init__(self, registry_url: str = "https://registry.example.com"):
        self.registry_url = registry_url
        self.images = {}
    
    def list_tags(self, image: str) -> List[str]:
        """Mock list image tags API call."""
        return ["latest", "v1.0.0", "v1.1.0"]
    
    def get_manifest(self, image: str, tag: str) -> Dict[str, Any]:
        """Mock get image manifest API call."""
        return {"schemaVersion": 2, "mediaType": "application/vnd.docker.distribution.manifest.v2+json"}
    
    def image_exists(self, image: str, tag: str = "latest") -> bool:
        """Check if image exists in registry."""
        return True


class MockKubernetesAPI:
    """Mock Kubernetes API for testing."""
    
    def __init__(self, kubeconfig: Optional[Dict[str, Any]] = None):
        self.kubeconfig = kubeconfig or {}
        self.resources = {}
    
    def apply_manifest(self, manifest: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Mock apply manifest API call."""
        kind = manifest.get("kind", "Unknown")
        name = manifest.get("metadata", {}).get("name", "unknown")
        return {
            "kind": kind,
            "name": name,
            "status": "dry_run" if dry_run else "applied"
        }
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Mock validate manifest API call."""
        if "apiVersion" not in manifest:
            return False, "Missing apiVersion"
        if "kind" not in manifest:
            return False, "Missing kind"
        return True, None
    
    def delete_resource(self, kind: str, name: str, namespace: str = "default") -> Dict[str, Any]:
        """Mock delete resource API call."""
        return {"kind": kind, "name": name, "status": "deleted"}


# =============================================================================
# Assertion Helpers
# =============================================================================

def assert_valid_output_format(content: str, format_type: str) -> None:
    """Assert that content matches expected format type."""
    validators = {
        "yaml": validate_yaml_syntax,
        "json": validate_json_syntax,
        "dockerfile": validate_dockerfile_syntax,
        "github_actions": validate_github_actions_workflow,
        "kubernetes": validate_kubernetes_manifest,
        "docker_compose": validate_docker_compose,
        "vercel": validate_vercel_config,
        "railway": validate_railway_config,
    }
    validator = validators.get(format_type)
    if validator:
        assert validator(content), f"Content does not match {format_type} format"


def assert_contains_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Assert that data contains all required fields."""
    missing = [f for f in required_fields if f not in data]
    assert not missing, f"Missing required fields: {missing}"


def assert_output_has_no_secrets(content: str) -> None:
    """Assert that output does not contain hardcoded secrets."""
    secret_patterns = [
        "password=", "secret=", "api_key=", "API_KEY=",
        "PRIVATE_KEY", "aws_access_key", "AWS_SECRET"
    ]
    for pattern in secret_patterns:
        # Allow placeholders like ${{ secrets.VAR }}
        lines = content.split("\n")
        for line in lines:
            if pattern in line and "${{" not in line and "secrets." not in line:
                assert False, f"Potential hardcoded secret found: {pattern}"


# =============================================================================
# Export all public fixtures and utilities
# =============================================================================

__all__ = [
    # Mock file system classes
    "MockFileSystem",
    "TempProjectDir",
    "mock_file_system_ctx",
    # Sample inputs
    "DOCKERFILE_GENERATOR_INPUTS",
    "GITHUB_ACTIONS_GENERATOR_INPUTS",
    "K8S_MANIFEST_GENERATOR_INPUTS",
    "DOCKER_COMPOSE_GENERATOR_INPUTS",
    "VERCEL_CONFIG_GENERATOR_INPUTS",
    "RAILWAY_CONFIG_GENERATOR_INPUTS",
    "INTEGRATION_TESTER_INPUTS",
    "ALL_GENERATOR_INPUTS",
    # Validation utilities
    "validate_yaml_syntax",
    "validate_json_syntax",
    "validate_dockerfile_syntax",
    "validate_github_actions_workflow",
    "validate_kubernetes_manifest",
    "validate_docker_compose",
    "validate_vercel_config",
    "validate_railway_config",
    # Mock classes
    "MockGitHubAPI",
    "MockDockerRegistry",
    "MockKubernetesAPI",
    # Assertion helpers
    "assert_valid_output_format",
    "assert_contains_required_fields",
    "assert_output_has_no_secrets",
]
