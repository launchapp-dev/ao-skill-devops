"""
Tests for dockerfile-generator skill and fixtures.

These tests validate the Dockerfile generator fixtures, test scenarios, and
ensure all test categories are properly configured.
"""

import os
import pytest
import yaml
from conftest import (
    MockFileSystem,
    TempProjectDir,
    validate_dockerfile_syntax,
    assert_valid_output_format,
    DOCKERFILE_GENERATOR_INPUTS,
)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDockerfileGeneratorInputs:
    """Tests for Dockerfile generator input fixtures."""

    def test_nodejs_multistage_input(self):
        """Test Node.js multistage input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["nodejs_multistage"]
        assert input_data["build_type"] == "multistage"
        assert input_data["language"] == "nodejs"
        assert input_data["language_version"] == "20.x"
        assert input_data["port"] == 3000
        assert input_data["user"] == "node"
        assert "healthcheck" in input_data
        assert "environment_variables" in input_data
        assert input_data["environment_variables"]["NODE_ENV"] == "production"

    def test_python_multistage_input(self):
        """Test Python multistage input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["python_multistage"]
        assert input_data["build_type"] == "multistage"
        assert input_data["language"] == "python"
        assert input_data["language_version"] == "3.12"
        assert input_data["port"] == 8000
        assert input_data["user"] == "app"
        assert "healthcheck" in input_data

    def test_go_multistage_input(self):
        """Test Go multistage input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["go_multistage"]
        assert input_data["build_type"] == "multistage"
        assert input_data["language"] == "go"
        assert input_data["language_version"] == "1.21"
        assert input_data["port"] == 8080
        assert input_data["user"] == "app"

    def test_rust_multistage_input(self):
        """Test Rust multistage input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["rust_multistage"]
        assert input_data["build_type"] == "multistage"
        assert input_data["language"] == "rust"
        assert input_data["language_version"] == "1.70"
        assert input_data["port"] == 8080
        assert "RUST_LOG" in input_data["environment_variables"]

    def test_static_site_input(self):
        """Test static site input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["static_site"]
        assert input_data["build_type"] == "multistage"
        assert input_data["language"] == "static"
        assert input_data["output_directory"] == "dist"
        assert input_data["port"] == 80
        assert input_data["user"] == "nginx"

    def test_distroless_input(self):
        """Test distroless input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["distroless"]
        assert input_data["build_type"] == "distroless"
        assert input_data["language"] == "nodejs"
        assert input_data["builder_image"] == "node:20-alpine"
        assert input_data["final_image"] == "gcr.io/distroless/nodejs20-debian11"
        assert input_data["user"] == "nonroot"

    def test_scratch_input(self):
        """Test scratch input fixture."""
        input_data = DOCKERFILE_GENERATOR_INPUTS["scratch"]
        assert input_data["build_type"] == "scratch"
        assert input_data["language"] == "go"
        assert input_data["language_version"] == "1.21"
        assert input_data["port"] == 8080


class TestDockerfileGeneratorTests:
    """Tests for dockerfile-generator-tests skill file."""

    def test_skill_file_loads(self):
        """Test that the skill file loads without errors."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        assert skill_data is not None
        assert skill_data["id"] == "ao.devops/dockerfile-generator-tests"
        assert skill_data["version"] == "0.1.0"
        assert skill_data["agent"] == "dockerfile-test-agent"

    def test_skill_has_capabilities(self):
        """Test that skill has all required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        capabilities = skill_data["capabilities"]
        assert capabilities["dockerfile_validation"] is True
        assert capabilities["multistage_tests"] is True
        assert capabilities["layer_optimization_tests"] is True
        assert capabilities["healthcheck_tests"] is True
        assert capabilities["non_root_user_tests"] is True
        assert capabilities["build_args_tests"] is True
        assert capabilities["env_vars_tests"] is True
        assert capabilities["base_image_tests"] is True

    def test_skill_has_test_categories(self):
        """Test that skill has all test categories."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        categories = skill_data["test_categories"]
        assert "multistage_builds" in categories
        assert "single_stage_builds" in categories
        assert "distroless_builds" in categories
        assert "scratch_builds" in categories
        assert "layer_caching" in categories
        assert "health_checks" in categories
        assert "non_root_users" in categories
        assert "build_arguments" in categories
        assert "environment_variables" in categories
        assert "base_images" in categories
        assert "static_sites" in categories
        assert "syntax_validation" in categories
        assert "copy_files" in categories
        assert "secrets_handling" in categories
        assert "edge_cases" in categories

    def test_multistage_builds_have_tests(self):
        """Test that multistage_builds has test cases for all languages."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["multistage_builds"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "multistage-nodejs" in language_ids
        assert "multistage-python" in language_ids
        assert "multistage-go" in language_ids
        assert "multistage-rust" in language_ids
        assert "multistage-deno" in language_ids
        assert "multistage-bun" in language_ids

    def test_health_checks_have_tests(self):
        """Test that health_checks has all required test cases."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["health_checks"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "healthcheck-http-curl" in language_ids
        assert "healthcheck-http-wget" in language_ids
        assert "healthcheck-tcp" in language_ids
        assert "healthcheck-disabled" in language_ids
        assert "healthcheck-defaults" in language_ids

    def test_non_root_users_have_tests(self):
        """Test that non_root_users has all required test cases."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["non_root_users"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "nonroot-nodejs" in language_ids
        assert "nonroot-python" in language_ids
        assert "nonroot-go" in language_ids
        assert "nonroot-create-group" in language_ids
        assert "nonroot-ownership" in language_ids
        assert "nonroot-distroless" in language_ids

    def test_base_images_have_tests(self):
        """Test that base_images has test cases for all languages."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["base_images"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "base-nodejs-alpine" in language_ids
        assert "base-nodejs-slim" in language_ids
        assert "base-python-slim" in language_ids
        assert "base-python-alpine" in language_ids
        assert "base-go-alpine" in language_ids
        assert "base-rust" in language_ids
        assert "base-static-nginx" in language_ids
        assert "base-deno" in language_ids
        assert "base-bun" in language_ids
        assert "base-custom" in language_ids

    def test_layer_caching_tests(self):
        """Test that layer_caching has required test cases."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["layer_caching"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "cache-node-dependencies" in language_ids
        assert "cache-python-dependencies" in language_ids
        assert "cache-go-modules" in language_ids
        assert "cache-minimize-layers" in language_ids

    def test_build_arguments_tests(self):
        """Test that build_arguments has required test cases."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["build_arguments"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "buildarg-version" in language_ids
        assert "buildarg-default-value" in language_ids
        assert "buildarg-labels" in language_ids
        assert "buildarg-no-args" in language_ids

    def test_environment_variables_tests(self):
        """Test that environment_variables has required test cases."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        tests = skill_data["test_categories"]["environment_variables"]["test_cases"]
        language_ids = [t["id"] for t in tests]
        assert "env-basic" in language_ids
        assert "env-multiple" in language_ids
        assert "env-production" in language_ids
        assert "env-runtime-only" in language_ids
        assert "env-empty" in language_ids

    def test_skill_has_test_scenarios(self):
        """Test that skill has test_scenarios for full integration."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        scenarios = skill_data["test_scenarios"]
        assert "nodejs_multistage_full" in scenarios
        assert "python_multistage_full" in scenarios
        assert "go_multistage_full" in scenarios
        assert "rust_multistage_full" in scenarios
        assert "static_site_nginx" in scenarios
        assert "distroless_full" in scenarios
        assert "scratch_go" in scenarios

    def test_skill_has_examples(self):
        """Test that skill has example inputs."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        examples = skill_data["examples"]
        assert "multistage_test" in examples
        assert "healthcheck_test" in examples
        assert "nonroot_test" in examples
        assert "layer_cache_test" in examples
        assert "base_image_test" in examples
        assert "full_validation" in examples

    def test_skill_has_input_schema(self):
        """Test that skill has input schema defined."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        schema = skill_data["input_schema"]
        assert "test_type" in schema
        assert schema["test_type"]["type"] == "string"
        assert "generated_dockerfile" in schema
        assert "validation_level" in schema

    def test_skill_has_output_schema(self):
        """Test that skill has output schema defined."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        output_schema = skill_data["output_schema"]
        assert "test_results" in output_schema
        assert "passed" in output_schema["test_results"]["properties"]
        assert "duration_ms" in output_schema["test_results"]["properties"]
        assert "errors" in output_schema["test_results"]["properties"]
        assert "validation_details" in output_schema["test_results"]["properties"]

    def test_skill_has_validation_rules(self):
        """Test that skill has validation rules defined."""
        with open(os.path.join(PROJECT_ROOT, "skills", "dockerfile-generator-tests.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        rules = skill_data["validation_rules"]
        assert "syntax" in rules
        assert "build_types" in rules
        assert "instructions" in rules
        assert "base_images" in rules


class TestDockerfileSyntaxValidation:
    """Tests for Dockerfile syntax validation."""

    def test_valid_multistage_dockerfile(self):
        """Test validation of valid multi-stage Dockerfile."""
        dockerfile = """
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
"""
        assert validate_dockerfile_syntax(dockerfile) is True

    def test_valid_single_stage_dockerfile(self):
        """Test validation of valid single-stage Dockerfile."""
        dockerfile = """
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
"""
        assert validate_dockerfile_syntax(dockerfile) is True

    def test_valid_distroless_dockerfile(self):
        """Test validation of valid distroless Dockerfile."""
        dockerfile = """
# syntax=docker/dockerfile:1.4
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian11
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
USER nonroot
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
"""
        assert validate_dockerfile_syntax(dockerfile) is True

    def test_valid_scratch_dockerfile(self):
        """Test validation of valid scratch Dockerfile."""
        dockerfile = """
FROM scratch
COPY --from=builder /bin/app /bin/app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
EXPOSE 8080
ENTRYPOINT ["/bin/app"]
"""
        assert validate_dockerfile_syntax(dockerfile) is True

    def test_invalid_instruction(self):
        """Test validation detects invalid instructions."""
        dockerfile = """
FROM node:20-alpine
INVALID_INSTRUCTION arg
"""
        assert validate_dockerfile_syntax(dockerfile) is False


class TestDockerfileFixtures:
    """Tests for Dockerfile-specific fixtures."""

    def test_all_dockerfile_inputs_have_required_fields(self):
        """Test that all Dockerfile inputs have required fields."""
        # Static site uses nginx as base, so it doesn't need start_command
        required_fields = ["build_type", "language", "port"]
        for name, input_data in DOCKERFILE_GENERATOR_INPUTS.items():
            for field in required_fields:
                assert field in input_data, f"Missing {field} in {name}"

    def test_all_dockerfile_inputs_have_start_command(self):
        """Test that most Dockerfile inputs have start_command (except static)."""
        for name, input_data in DOCKERFILE_GENERATOR_INPUTS.items():
            if name != "static_site":
                assert "start_command" in input_data, f"Missing start_command in {name}"

    def test_healthcheck_fixtures_have_required_fields(self):
        """Test that healthcheck fixtures have required fields."""
        required_fields = ["cmd", "interval", "timeout", "retries"]
        for name, input_data in DOCKERFILE_GENERATOR_INPUTS.items():
            if "healthcheck" in input_data and input_data["healthcheck"] is not None:
                for field in required_fields:
                    assert field in input_data["healthcheck"], f"Missing {field} in {name} healthcheck"

    def test_base_images_correct_for_languages(self):
        """Test that base images are correctly associated with languages."""
        assert DOCKERFILE_GENERATOR_INPUTS["nodejs_multistage"]["language"] == "nodejs"
        assert DOCKERFILE_GENERATOR_INPUTS["python_multistage"]["language"] == "python"
        assert DOCKERFILE_GENERATOR_INPUTS["go_multistage"]["language"] == "go"
        assert DOCKERFILE_GENERATOR_INPUTS["rust_multistage"]["language"] == "rust"
        assert DOCKERFILE_GENERATOR_INPUTS["static_site"]["language"] == "static"

    def test_distroless_has_custom_images(self):
        """Test that distroless fixture has custom builder and final images."""
        distroless = DOCKERFILE_GENERATOR_INPUTS["distroless"]
        assert "builder_image" in distroless
        assert "final_image" in distroless
        assert "distroless" in distroless["final_image"]

    def test_scratch_uses_go_language(self):
        """Test that scratch fixture uses Go for static binary builds."""
        scratch = DOCKERFILE_GENERATOR_INPUTS["scratch"]
        assert scratch["language"] == "go"
        assert "ldflags" in scratch["build_command"]

    def test_static_site_uses_nginx(self):
        """Test that static site fixture uses nginx user."""
        static = DOCKERFILE_GENERATOR_INPUTS["static_site"]
        assert static["user"] == "nginx"
        assert static["output_directory"] == "dist"


class TestDockerfileAgentExists:
    """Tests for dockerfile-agent in agents.yaml."""

    def test_dockerfile_agent_exists(self):
        """Test that dockerfile-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "dockerfile-agent" in agents_data["agents"]

    def test_dockerfile_agent_has_description(self):
        """Test that dockerfile-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["dockerfile-agent"]
        assert "description" in agent
        assert "Dockerfile" in agent["description"]

    def test_dockerfile_agent_has_capabilities(self):
        """Test that dockerfile-agent has required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["dockerfile-agent"]
        capabilities = agent["capabilities"]
        assert capabilities["dockerfile_generation"] is True
        assert capabilities["multistage_support"] is True
        assert capabilities["layer_optimization"] is True

    def test_dockerfile_test_agent_exists(self):
        """Test that dockerfile-test-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "dockerfile-test-agent" in agents_data["agents"]

    def test_dockerfile_test_agent_has_description(self):
        """Test that dockerfile-test-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["dockerfile-test-agent"]
        assert "description" in agent
        assert "Dockerfile" in agent["description"]
        assert "test" in agent["description"].lower()

    def test_dockerfile_test_agent_has_capabilities(self):
        """Test that dockerfile-test-agent has required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["dockerfile-test-agent"]
        capabilities = agent["capabilities"]
        assert capabilities["testing"] is True
        assert capabilities["validation"] is True
        assert capabilities["dockerfile_testing"] is True
        assert capabilities["syntax_validation"] is True


class TestPackManifest:
    """Tests for pack.toml manifest."""

    def test_pack_toml_loads(self):
        """Test that pack.toml loads without errors."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert pack_data is not None
        assert pack_data["schema"] == "ao.pack.v1"
        assert pack_data["id"] == "ao.devops"
        assert pack_data["kind"] == "skill-pack"

    def test_dockerfile_generator_exported(self):
        """Test that dockerfile-generator is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/dockerfile-generator" in pack_data["skills"]["exports"]

    def test_dockerfile_generator_tests_exported(self):
        """Test that dockerfile-generator-tests is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/dockerfile-generator-tests" in pack_data["skills"]["exports"]

    def test_skills_export_count(self):
        """Test that all skills are properly exported."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        exports = pack_data["skills"]["exports"]
        # Should have all original skills plus the new one
        assert len(exports) >= 13  # Original count + 1 new
