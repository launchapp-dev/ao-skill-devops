"""
Tests for conftest.py fixtures and utilities.

These tests verify that all fixtures are properly configured and utilities work correctly.
"""

import pytest
from conftest import (
    MockFileSystem,
    TempProjectDir,
    mock_file_system_ctx,
    validate_yaml_syntax,
    validate_json_syntax,
    validate_dockerfile_syntax,
    validate_github_actions_workflow,
    validate_kubernetes_manifest,
    validate_docker_compose,
    assert_valid_output_format,
    assert_contains_required_fields,
    assert_output_has_no_secrets,
    DOCKERFILE_GENERATOR_INPUTS,
    GITHUB_ACTIONS_GENERATOR_INPUTS,
    K8S_MANIFEST_GENERATOR_INPUTS,
    DOCKER_COMPOSE_GENERATOR_INPUTS,
    VERCEL_CONFIG_GENERATOR_INPUTS,
    RAILWAY_CONFIG_GENERATOR_INPUTS,
    ALL_GENERATOR_INPUTS,
)


class TestMockFileSystem:
    """Tests for MockFileSystem class."""
    
    def test_write_and_read(self):
        """Test writing and reading files."""
        fs = MockFileSystem()
        fs.write("/test/file.txt", "Hello, World!")
        assert fs.read("/test/file.txt") == "Hello, World!"
    
    def test_exists(self):
        """Test file existence check."""
        fs = MockFileSystem()
        fs.write("/test/file.txt", "content")
        assert fs.exists("/test/file.txt")
        assert not fs.exists("/nonexistent.txt")
    
    def test_is_file_is_dir(self):
        """Test is_file and is_dir methods."""
        fs = MockFileSystem()
        fs.write("/test/file.txt", "content")
        fs.makedirs("/test/dir")
        assert fs.is_file("/test/file.txt")
        assert fs.is_dir("/test/dir")
        assert not fs.is_file("/test/dir")
        assert not fs.is_dir("/test/file.txt")
    
    def test_list_dir(self):
        """Test directory listing."""
        fs = MockFileSystem()
        fs.write("/test/file1.txt", "content1")
        fs.write("/test/file2.txt", "content2")
        fs.makedirs("/test/subdir")
        files = fs.list_dir("/test")
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "subdir" in files
    
    def test_remove(self):
        """Test file removal."""
        fs = MockFileSystem()
        fs.write("/test/file.txt", "content")
        fs.remove("/test/file.txt")
        assert not fs.exists("/test/file.txt")
    
    def test_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        fs = MockFileSystem()
        with pytest.raises(FileNotFoundError):
            fs.read("/nonexistent.txt")


class TestTempProjectDir:
    """Tests for TempProjectDir context manager."""
    
    def test_creates_temp_directory(self):
        """Test that temporary directory is created."""
        with TempProjectDir() as temp_dir:
            assert temp_dir.exists()
            assert temp_dir.is_dir()
    
    def test_creates_structure(self):
        """Test that directory structure is created."""
        structure = {
            "src": {
                "index.ts": "console.log('test');",
                "app.ts": "export const app = {};"
            },
            "package.json": '{"name": "test"}'
        }
        with TempProjectDir(structure) as temp_dir:
            assert (temp_dir / "src" / "index.ts").exists()
            assert (temp_dir / "package.json").exists()
            assert (temp_dir / "src" / "index.ts").read_text() == "console.log('test');"
    
    def test_cleans_up_on_exit(self):
        """Test that directory is cleaned up after exit."""
        temp_path = None
        with TempProjectDir() as temp_dir:
            temp_path = temp_dir
            assert temp_dir.exists()
        assert not temp_path.exists()


class TestMockFileSystemContextManager:
    """Tests for mock_file_system_ctx."""
    
    def test_context_manager_yields_fs(self):
        """Test that context manager yields MockFileSystem."""
        with mock_file_system_ctx() as fs:
            assert isinstance(fs, MockFileSystem)
    
    def test_initial_files(self):
        """Test initialization with files."""
        initial = {
            "/test/file.txt": "initial content",
            "/another.txt": "more content"
        }
        with mock_file_system_ctx(initial) as fs:
            assert fs.read("/test/file.txt") == "initial content"
            assert fs.read("/another.txt") == "more content"


class TestValidationUtilities:
    """Tests for validation utility functions."""
    
    def test_validate_yaml_syntax_valid(self):
        """Test YAML validation with valid content."""
        yaml_content = """
name: test
version: 1.0.0
services:
  - name: web
    image: nginx
"""
        assert validate_yaml_syntax(yaml_content) is True
    
    def test_validate_yaml_syntax_invalid(self):
        """Test YAML validation with invalid content."""
        # Truly invalid YAML - missing colon after key
        invalid_yaml = """
name: test
version
"""
        assert validate_yaml_syntax(invalid_yaml) is False
    
    def test_validate_json_syntax_valid(self):
        """Test JSON validation with valid content."""
        json_content = '{"name": "test", "version": "1.0.0"}'
        assert validate_json_syntax(json_content) is True
    
    def test_validate_json_syntax_invalid(self):
        """Test JSON validation with invalid content."""
        invalid_json = '{"name": "test", invalid}'
        assert validate_json_syntax(invalid_json) is False
    
    def test_validate_dockerfile_syntax_valid(self):
        """Test Dockerfile validation with valid content."""
        dockerfile = """
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
"""
        assert validate_dockerfile_syntax(dockerfile) is True
    
    def test_validate_dockerfile_syntax_invalid(self):
        """Test Dockerfile validation with invalid instruction."""
        dockerfile = """
FROM node:20-alpine
INVALID_INSTRUCTION arg
"""
        assert validate_dockerfile_syntax(dockerfile) is False
    
    def test_validate_github_actions_workflow(self):
        """Test GitHub Actions workflow validation."""
        workflow = """
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
"""
        assert validate_github_actions_workflow(workflow) is True
    
    def test_validate_kubernetes_manifest(self):
        """Test Kubernetes manifest validation."""
        manifest = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
"""
        assert validate_kubernetes_manifest(manifest) is True
    
    def test_validate_docker_compose(self):
        """Test Docker Compose file validation."""
        compose = """
version: '3.8'
services:
  web:
    image: nginx
"""
        assert validate_docker_compose(compose) is True


class TestAllGeneratorInputs:
    """Tests that all generator input fixtures are properly configured."""
    
    def test_dockerfile_inputs(self):
        """Test Dockerfile generator inputs."""
        assert "nodejs_multistage" in DOCKERFILE_GENERATOR_INPUTS
        assert "python_multistage" in DOCKERFILE_GENERATOR_INPUTS
        assert "go_multistage" in DOCKERFILE_GENERATOR_INPUTS
        
        # Verify structure
        nodejs = DOCKERFILE_GENERATOR_INPUTS["nodejs_multistage"]
        assert nodejs["build_type"] == "multistage"
        assert nodejs["language"] == "nodejs"
        assert "healthcheck" in nodejs
    
    def test_github_actions_inputs(self):
        """Test GitHub Actions generator inputs."""
        assert "nodejs_ci" in GITHUB_ACTIONS_GENERATOR_INPUTS
        assert "python_cicd" in GITHUB_ACTIONS_GENERATOR_INPUTS
        assert "go_cd" in GITHUB_ACTIONS_GENERATOR_INPUTS
        
        # Verify structure
        nodejs = GITHUB_ACTIONS_GENERATOR_INPUTS["nodejs_ci"]
        assert nodejs["environment"] == "nodejs"
        assert "lint" in nodejs["steps"]
    
    def test_k8s_manifest_inputs(self):
        """Test Kubernetes manifest generator inputs."""
        assert "deployment" in K8S_MANIFEST_GENERATOR_INPUTS
        assert "service" in K8S_MANIFEST_GENERATOR_INPUTS
        assert "ingress" in K8S_MANIFEST_GENERATOR_INPUTS
        assert "configmap" in K8S_MANIFEST_GENERATOR_INPUTS
        assert "secret" in K8S_MANIFEST_GENERATOR_INPUTS
        
        # Verify structure
        deployment = K8S_MANIFEST_GENERATOR_INPUTS["deployment"]
        assert deployment["manifest_type"] == "deployment"
        assert "spec" in deployment
    
    def test_docker_compose_inputs(self):
        """Test Docker Compose generator inputs."""
        assert "basic" in DOCKER_COMPOSE_GENERATOR_INPUTS
        assert "with_db" in DOCKER_COMPOSE_GENERATOR_INPUTS
        
        # Verify structure
        compose = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]
        assert "services" in compose
        assert len(compose["services"]) >= 2
    
    def test_vercel_config_inputs(self):
        """Test Vercel config generator inputs."""
        assert "static_site" in VERCEL_CONFIG_GENERATOR_INPUTS
        assert "nextjs" in VERCEL_CONFIG_GENERATOR_INPUTS
        
        # Verify structure
        vercel = VERCEL_CONFIG_GENERATOR_INPUTS["nextjs"]
        assert vercel["deployment_type"] == "framework"
        assert vercel["framework"] == "nextjs"
    
    def test_railway_config_inputs(self):
        """Test Railway config generator inputs."""
        assert "docker" in RAILWAY_CONFIG_GENERATOR_INPUTS
        assert "nixpacks_node" in RAILWAY_CONFIG_GENERATOR_INPUTS
        assert "monorepo" in RAILWAY_CONFIG_GENERATOR_INPUTS
        
        # Verify structure
        railway = RAILWAY_CONFIG_GENERATOR_INPUTS["docker"]
        assert railway["deployment_type"] == "docker"
        assert "port" in railway
    
    def test_all_inputs_combined(self):
        """Test that ALL_GENERATOR_INPUTS contains all generator types."""
        expected_types = [
            "dockerfile",
            "github_actions",
            "k8s_manifest",
            "docker_compose",
            "vercel_config",
            "railway_config"
        ]
        for generator_type in expected_types:
            assert generator_type in ALL_GENERATOR_INPUTS


class TestParametrizedFixtures:
    """Tests for parametrized fixtures."""
    
    def test_dockerfile_input_fixture(self, dockerfile_input):
        """Test dockerfile_input parametrized fixture."""
        assert "build_type" in dockerfile_input
        assert "language" in dockerfile_input
    
    def test_github_actions_input_fixture(self, github_actions_input):
        """Test github_actions_input parametrized fixture."""
        assert "environment" in github_actions_input
        assert "workflow_type" in github_actions_input
    
    def test_k8s_manifest_input_fixture(self, k8s_manifest_input):
        """Test k8s_manifest_input parametrized fixture."""
        assert "manifest_type" in k8s_manifest_input
        # Most K8s resources use 'name', but helm uses 'chart_name' and kustomize uses 'base_chart'
        manifest_type = k8s_manifest_input.get("manifest_type")
        if manifest_type in ("helm", "kustomize"):
            assert "chart_name" in k8s_manifest_input or "base_chart" in k8s_manifest_input
        else:
            assert "name" in k8s_manifest_input
    
    def test_docker_compose_input_fixture(self, docker_compose_input):
        """Test docker_compose_input parametrized fixture."""
        assert "services" in docker_compose_input
    
    def test_vercel_config_input_fixture(self, vercel_config_input):
        """Test vercel_config_input parametrized fixture."""
        assert "deployment_type" in vercel_config_input
    
    def test_railway_config_input_fixture(self, railway_config_input):
        """Test railway_config_input parametrized fixture."""
        assert "deployment_type" in railway_config_input


class TestAssertionHelpers:
    """Tests for assertion helper functions."""
    
    def test_assert_valid_output_format_yaml(self):
        """Test format assertion for YAML."""
        yaml_content = """
name: test
version: 1.0.0
"""
        assert_valid_output_format(yaml_content, "yaml")
    
    def test_assert_valid_output_format_json(self):
        """Test format assertion for JSON."""
        json_content = '{"name": "test"}'
        assert_valid_output_format(json_content, "json")
    
    def test_assert_contains_required_fields(self):
        """Test required fields assertion."""
        data = {"name": "test", "version": "1.0.0", "extra": "field"}
        assert_contains_required_fields(data, ["name", "version"])
    
    def test_assert_contains_required_fields_missing(self):
        """Test required fields assertion with missing fields."""
        data = {"name": "test"}
        with pytest.raises(AssertionError):
            assert_contains_required_fields(data, ["name", "version"])
    
    def test_assert_output_has_no_secrets_safe(self):
        """Test secret detection with safe content."""
        safe_content = """
FROM node:20
ENV NODE_ENV=production
ARG BUILD_ARG
"""
        assert_output_has_no_secrets(safe_content)  # Should not raise
    
    def test_assert_output_has_no_secrets_with_placeholder(self):
        """Test secret detection allows placeholders."""
        safe_content = """
ENV DATABASE_URL=${{ secrets.DATABASE_URL }}
"""
        assert_output_has_no_secrets(safe_content)  # Should not raise


class TestProjectFixtures:
    """Tests for project-related fixtures."""
    
    def test_temp_project_fixture(self, temp_project):
        """Test temp_project fixture."""
        assert temp_project.exists()
        assert temp_project.is_dir()
    
    def test_temp_project_with_structure(self, temp_project_with_structure):
        """Test temp_project_with_structure fixture."""
        assert (temp_project_with_structure / "package.json").exists()
        assert (temp_project_with_structure / "src" / "index.ts").exists()


class TestSpecificInputs:
    """Tests for specific generator input configurations."""
    
    def test_dockerfile_nodejs_has_healthcheck(self):
        """Verify Node.js Dockerfile has healthcheck."""
        from conftest import DOCKERFILE_NODEJS_MULTISTAGE
        assert "healthcheck" in DOCKERFILE_NODEJS_MULTISTAGE
        assert DOCKERFILE_NODEJS_MULTISTAGE["healthcheck"]["cmd"] is not None
    
    def test_dockerfile_distroless_has_final_image(self):
        """Verify distroless Dockerfile has final_image."""
        from conftest import DOCKERFILE_DISTROLESS
        assert DOCKERFILE_DISTROLESS["build_type"] == "distroless"
        assert "final_image" in DOCKERFILE_DISTROLESS
    
    def test_github_actions_matrix_config(self):
        """Verify matrix configuration in GitHub Actions."""
        from conftest import GITHUB_ACTIONS_NODEJS_MATRIX
        assert "matrix" in GITHUB_ACTIONS_NODEJS_MATRIX
        assert "os" in GITHUB_ACTIONS_NODEJS_MATRIX["matrix"]
    
    def test_k8s_deployment_has_replicas(self):
        """Verify K8s deployment has replica specification."""
        from conftest import K8S_DEPLOYMENT
        assert K8S_DEPLOYMENT["manifest_type"] == "deployment"
        assert K8S_DEPLOYMENT["spec"]["replicas"] == 3
    
    def test_docker_compose_has_networks_and_volumes(self):
        """Verify Docker Compose has networks and volumes."""
        from conftest import DOCKER_COMPOSE_WITH_DB
        assert "networks" in DOCKER_COMPOSE_WITH_DB
        assert "volumes" in DOCKER_COMPOSE_WITH_DB
    
    def test_vercel_nextjs_has_routes(self):
        """Verify Vercel Next.js has routes configuration."""
        from conftest import VERCEL_NEXTJS
        assert "routes" in VERCEL_NEXTJS
        assert len(VERCEL_NEXTJS["routes"]) > 0
    
    def test_railway_monorepo_has_services(self):
        """Verify Railway monorepo has multiple services."""
        from conftest import RAILWAY_MONOREPO
        assert "services" in RAILWAY_MONOREPO
        assert len(RAILWAY_MONOREPO["services"]) >= 3
