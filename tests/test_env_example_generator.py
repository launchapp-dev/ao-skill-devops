"""
Tests for env-example-generator skill and fixtures.

These tests validate the env-example-generator skill file, agent, workflows,
fixtures, and ensure all framework types are properly covered.
"""

import os
import pytest
import yaml
from conftest import (
    MockFileSystem,
    TempProjectDir,
    validate_env_example,
    assert_valid_output_format,
    ENV_EXAMPLE_GENERATOR_INPUTS,
)


# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestEnvExampleGeneratorInputs:
    """Tests for env-example-generator input fixtures."""

    def test_basic_input(self):
        """Test basic env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["basic"]
        assert input_data["project_name"] == "my-api"
        assert input_data["environment_type"] == "generic"
        assert "split_secrets" in input_data
        assert "include_comments" in input_data
        assert "include_validation" in input_data
        assert "format" in input_data
        assert len(input_data["variables"]) == 3

    def test_nodejs_input(self):
        """Test Node.js env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["nodejs"]
        assert input_data["environment_type"] == "nodejs"
        assert input_data["project_name"] == "express-api"
        assert input_data["framework_presets"]["database"] is True
        assert input_data["framework_presets"]["auth"] is True
        assert input_data["framework_presets"]["monitoring"] is True
        assert input_data["split_secrets"] is True

    def test_python_input(self):
        """Test Python env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["python"]
        assert input_data["environment_type"] == "python"
        assert input_data["project_name"] == "flask-api"
        assert input_data["framework_presets"]["database"] is True
        assert input_data["framework_presets"]["cache"] is True
        assert input_data["framework_presets"]["email"] is True
        assert input_data["include_validation"] is True

    def test_go_input(self):
        """Test Go env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["go"]
        assert input_data["environment_type"] == "go"
        assert input_data["project_name"] == "go-api"
        assert "GOPROXY" in [v["name"] for v in input_data["variables"]]
        assert "GOCACHE" in [v["name"] for v in input_data["variables"]]

    def test_ruby_input(self):
        """Test Ruby env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["ruby"]
        assert input_data["environment_type"] == "ruby"
        assert input_data["project_name"] == "rails-app"
        assert "RAILS_ENV" in [v["name"] for v in input_data["variables"]]
        assert "SECRET_KEY_BASE" in [v["name"] for v in input_data["variables"]]

    def test_php_input(self):
        """Test PHP env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["php"]
        assert input_data["environment_type"] == "php"
        assert input_data["project_name"] == "laravel-app"
        assert "APP_ENV" in [v["name"] for v in input_data["variables"]]

    def test_java_input(self):
        """Test Java env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["java"]
        assert input_data["environment_type"] == "java"
        assert input_data["project_name"] == "spring-boot-app"
        assert "SPRING_PROFILES_ACTIVE" in [v["name"] for v in input_data["variables"]]

    def test_rust_input(self):
        """Test Rust env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["rust"]
        assert input_data["environment_type"] == "rust"
        assert input_data["project_name"] == "rust-service"
        assert "RUST_LOG" in [v["name"] for v in input_data["variables"]]

    def test_docker_input(self):
        """Test Docker env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["docker"]
        assert input_data["environment_type"] == "docker"
        assert "BUILD_DATE" in [v["name"] for v in input_data["variables"]]
        assert "SOURCE_COMMIT" in [v["name"] for v in input_data["variables"]]

    def test_kubernetes_input(self):
        """Test Kubernetes env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["kubernetes"]
        assert input_data["environment_type"] == "kubernetes"
        assert input_data["project_name"] == "k8s-app"
        assert "POD_NAME" in [v["name"] for v in input_data["variables"]]
        assert "NAMESPACE" in [v["name"] for v in input_data["variables"]]

    def test_deno_input(self):
        """Test Deno env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["deno"]
        assert input_data["environment_type"] == "deno"
        assert input_data["project_name"] == "deno-api"
        assert "DENO_ENV" in [v["name"] for v in input_data["variables"]]

    def test_bun_input(self):
        """Test Bun env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["bun"]
        assert input_data["environment_type"] == "bun"
        assert input_data["project_name"] == "bun-api"
        assert input_data["framework_presets"]["auth"] is True

    def test_fullstack_input(self):
        """Test fullstack env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["fullstack"]
        assert input_data["project_name"] == "fullstack-app"
        # All presets should be enabled
        assert all(input_data["framework_presets"].values())
        assert input_data["split_secrets"] is True

    def test_json_format_input(self):
        """Test JSON format env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["json_format"]
        assert input_data["format"] == "json"
        assert "APP_NAME" in [v["name"] for v in input_data["variables"]]
        assert "DEBUG" in [v["name"] for v in input_data["variables"]]

    def test_yaml_format_input(self):
        """Test YAML format env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["yaml_format"]
        assert input_data["format"] == "yaml"

    def test_toml_format_input(self):
        """Test TOML format env-example input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["toml_format"]
        assert input_data["format"] == "toml"

    def test_no_split_input(self):
        """Test no split secrets input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["no_split"]
        assert input_data["split_secrets"] is False

    def test_no_comments_input(self):
        """Test no comments input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["no_comments"]
        assert input_data["include_comments"] is False

    def test_validation_input(self):
        """Test validation hints input fixture."""
        input_data = ENV_EXAMPLE_GENERATOR_INPUTS["validation"]
        assert input_data["include_validation"] is True
        variables_with_validation = [v for v in input_data["variables"] if "validation" in v]
        assert len(variables_with_validation) > 0


class TestEnvExampleGeneratorSkill:
    """Tests for env-example-generator skill file."""

    def test_skill_file_loads(self):
        """Test that the skill file loads without errors."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        assert skill_data is not None
        assert skill_data["id"] == "ao.devops/env-example-generator"
        assert skill_data["version"] == "0.1.0"
        assert skill_data["agent"] == "env-example-generator-agent"

    def test_skill_has_environment_types(self):
        """Test that skill has all required environment types."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        env_types = skill_data["environment_types"]
        expected_types = ["nodejs", "python", "go", "deno", "bun", "ruby", "php", "java", "rust", "docker", "kubernetes", "generic"]
        for env_type in expected_types:
            assert env_type in env_types, f"Missing environment type: {env_type}"

    def test_skill_has_features(self):
        """Test that skill has all required features."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        features = skill_data["features"]
        expected_features = ["type_hints", "descriptions", "secrets_identification", "public_private_split", "framework_presets", "default_values", "validation_hints", "multi_framework_support"]
        for feature in expected_features:
            assert feature in features, f"Missing feature: {feature}"

    def test_skill_has_capabilities(self):
        """Test that skill has all required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        capabilities = skill_data["capabilities"]
        assert capabilities["env_example_generation"] is True
        assert capabilities["secrets_handling"] is True
        assert capabilities["framework_detection"] is True
        assert capabilities["multi_format_output"] is True
        assert capabilities["variable_validation"] is True
        assert capabilities["documentation_generation"] is True

    def test_skill_has_input_schema(self):
        """Test that skill has complete input schema."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        schema = skill_data["input_schema"]
        # Check main fields
        assert "environment_type" in schema
        assert "project_name" in schema
        assert "variables" in schema
        assert "framework_presets" in schema
        assert "split_secrets" in schema
        assert "include_validation" in schema
        assert "include_comments" in schema
        assert "format" in schema

    def test_input_schema_has_environment_type_enum(self):
        """Test that input schema has correct environment_type enum."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        env_type_schema = skill_data["input_schema"]["environment_type"]
        assert "enum" in env_type_schema
        assert "nodejs" in env_type_schema["enum"]
        assert "python" in env_type_schema["enum"]
        assert "go" in env_type_schema["enum"]

    def test_input_schema_has_framework_presets(self):
        """Test that input schema has framework presets."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        presets_schema = skill_data["input_schema"]["framework_presets"]["properties"]
        expected_presets = ["database", "cache", "auth", "storage", "email", "monitoring", "queue"]
        for preset in expected_presets:
            assert preset in presets_schema, f"Missing framework preset: {preset}"

    def test_input_schema_has_variable_types(self):
        """Test that input schema has correct variable types."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        var_schema = skill_data["input_schema"]["variables"]["items"]["properties"]["type"]
        expected_types = ["string", "number", "boolean", "url", "path", "email", "port", "secret", "array"]
        for var_type in expected_types:
            assert var_type in var_schema["enum"], f"Missing variable type: {var_type}"

    def test_input_schema_has_format_options(self):
        """Test that input schema has correct format options."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        format_schema = skill_data["input_schema"]["format"]
        assert "enum" in format_schema
        assert "env" in format_schema["enum"]
        assert "json" in format_schema["enum"]
        assert "yaml" in format_schema["enum"]
        assert "toml" in format_schema["enum"]

    def test_skill_has_examples(self):
        """Test that skill has example inputs."""
        with open(os.path.join(PROJECT_ROOT, "skills", "env-example-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        examples = skill_data["examples"]
        assert "basic" in examples
        assert "nodejs_preset" in examples
        assert "python_preset" in examples
        assert "fullstack" in examples


class TestEnvExampleGeneratorAgent:
    """Tests for env-example-generator-agent in agents.yaml."""

    def test_agent_exists(self):
        """Test that env-example-generator-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "env-example-generator-agent" in agents_data["agents"]

    def test_agent_has_description(self):
        """Test that env-example-generator-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["env-example-generator-agent"]
        assert "description" in agent
        assert "env" in agent["description"].lower() or ".env" in agent["description"].lower()

    def test_agent_has_capabilities(self):
        """Test that env-example-generator-agent has required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["env-example-generator-agent"]
        capabilities = agent["capabilities"]
        assert capabilities["env_example_generation"] is True
        assert capabilities["secrets_handling"] is True
        assert capabilities["framework_detection"] is True

    def test_agent_has_system_prompt(self):
        """Test that env-example-generator-agent has a system prompt."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["env-example-generator-agent"]
        assert "system_prompt" in agent
        prompt = agent["system_prompt"]
        # Check that prompt covers key areas
        assert "framework" in prompt.lower() or "environment" in prompt.lower()
        assert "secret" in prompt.lower()

    def test_agent_system_prompt_covers_all_environment_types(self):
        """Test that env-example-generator-agent system prompt covers all 12 environment types."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["env-example-generator-agent"]
        prompt = agent["system_prompt"]
        # All 12 environment types from the skill
        expected_types = ["Node.js", "Python", "Go", "Ruby", "PHP", "Java", "Rust", "Deno", "Bun", "Docker", "Kubernetes", "Generic"]
        for env_type in expected_types:
            assert env_type in prompt, f"Agent prompt should document {env_type} environment type"


class TestEnvExampleGeneratorWorkflows:
    """Tests for env-example-generator workflows in skill-pack.yaml."""

    def test_env_example_workflow_exists(self):
        """Test that ao.devops/env-example workflow exists."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        workflow_ids = [w["id"] for w in workflows_data["workflows"]]
        assert "ao.devops/env-example" in workflow_ids

    def test_env_example_with_tests_workflow_exists(self):
        """Test that ao.devops/env-example-with-tests workflow exists."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        workflow_ids = [w["id"] for w in workflows_data["workflows"]]
        assert "ao.devops/env-example-with-tests" in workflow_ids

    def test_env_example_phase_exists(self):
        """Test that env-example-generate phase exists."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        phases = workflows_data["phases"]
        assert "env-example-generate" in phases

    def test_env_example_phase_uses_correct_agent(self):
        """Test that env-example-generate phase uses env-example-generator-agent."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        phase = workflows_data["phases"]["env-example-generate"]
        assert phase["agent"] == "env-example-generator-agent"

    def test_env_example_phase_has_input_schema(self):
        """Test that env-example-generate phase has input schema."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        phase = workflows_data["phases"]["env-example-generate"]
        assert "input_schema" in phase
        schema = phase["input_schema"]
        assert "environment_type" in schema
        assert "project_name" in schema
        assert "variables" in schema
        assert "framework_presets" in schema

    def test_env_example_workflow_has_correct_phases(self):
        """Test that ao.devops/env-example workflow has correct phases."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        workflow = next((w for w in workflows_data["workflows"] if w["id"] == "ao.devops/env-example"), None)
        assert workflow is not None
        assert "phases" in workflow
        phases = workflow["phases"]
        assert "env-example-generate" in phases
        assert "push-branch" in phases
        assert "create-pr" in phases
        assert "pr-review" in phases

    def test_env_example_with_tests_workflow_has_integration_test(self):
        """Test that ao.devops/env-example-with-tests workflow has integration-test phase."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        workflow = next((w for w in workflows_data["workflows"] if w["id"] == "ao.devops/env-example-with-tests"), None)
        assert workflow is not None
        assert "phases" in workflow
        phases = workflow["phases"]
        assert "env-example-generate" in phases
        assert "integration-test" in phases

    def test_integration_test_phase_uses_integration_tester_agent(self):
        """Test that integration-test phase uses integration-tester-agent, not vercel-config-test-agent."""
        with open(os.path.join(PROJECT_ROOT, "workflows", "skill-pack.yaml"), "r") as f:
            workflows_data = yaml.safe_load(f)
        phases = workflows_data["phases"]
        assert "integration-test" in phases, "integration-test phase should exist"
        phase = phases["integration-test"]
        # Should use integration-tester-agent, not vercel-config-test-agent
        assert phase["agent"] == "integration-tester-agent", \
            f"integration-test phase should use integration-tester-agent, got: {phase['agent']}"
        # Verify it's NOT using vercel-config-test-agent
        assert phase["agent"] != "vercel-config-test-agent", \
            "integration-test phase should not use vercel-config-test-agent"


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

    def test_env_example_generator_exported(self):
        """Test that env-example-generator is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/env-example-generator" in pack_data["skills"]["exports"]

    def test_env_example_workflow_exported(self):
        """Test that env-example workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/env-example" in pack_data["workflows"]["exports"]

    def test_env_example_with_tests_workflow_exported(self):
        """Test that env-example-with-tests workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/env-example-with-tests" in pack_data["workflows"]["exports"]

    def test_skills_export_count(self):
        """Test that all skills are properly exported."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        exports = pack_data["skills"]["exports"]
        # Should have all original skills including env-example-generator
        assert len(exports) >= 14  # Original count + env-example-generator

    def test_workflows_export_count(self):
        """Test that all workflows are properly exported."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        exports = pack_data["workflows"]["exports"]
        # Should have all original workflows including env-example workflows
        assert len(exports) >= 17  # Original count + env-example workflows


class TestEnvExampleValidation:
    """Tests for env-example validation functions."""

    def test_validate_env_example_valid(self):
        """Test validation of valid env example."""
        content = """
# Application Configuration
NODE_ENV=development
PORT=3000
DATABASE_URL=
"""
        assert validate_env_example(content, "env") is True

    def test_validate_env_example_with_comments(self):
        """Test validation of env example with comments."""
        content = """
# This is a comment
NODE_ENV=development
# Another comment
PORT=3000
"""
        assert validate_env_example(content, "env") is True

    def test_validate_env_example_with_sections(self):
        """Test validation of env example with sections."""
        content = """
# PUBLIC VARIABLES
NODE_ENV=development
PORT=3000

# PRIVATE VARIABLES
DATABASE_URL=
API_KEY=
"""
        assert validate_env_example(content, "env") is True

    def test_validate_env_example_json(self):
        """Test validation of JSON format."""
        content = '{"NODE_ENV": "development", "PORT": 3000}'
        assert validate_env_example(content, "json") is True

    def test_validate_env_example_yaml(self):
        """Test validation of YAML format."""
        content = """
NODE_ENV: development
PORT: 3000
"""
        assert validate_env_example(content, "yaml") is True

    def test_validate_env_example_toml(self):
        """Test validation of TOML format."""
        content = """
[default]
NODE_ENV = "development"
PORT = 3000
"""
        assert validate_env_example(content, "toml") is True


class TestEnvExampleFixtures:
    """Tests for env-example-specific fixtures."""

    def test_all_inputs_have_project_name(self):
        """Test that all env-example inputs have project_name."""
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            assert "project_name" in input_data, f"Missing project_name in {name}"

    def test_all_inputs_have_format(self):
        """Test that all env-example inputs have format field."""
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            assert "format" in input_data, f"Missing format in {name}"

    def test_variables_have_required_name(self):
        """Test that all variables have required name field."""
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            if "variables" in input_data:
                for var in input_data["variables"]:
                    assert "name" in var, f"Missing name in {name} variables"

    def test_secret_variables_have_empty_values(self):
        """Test that secrets are properly marked."""
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            if "variables" in input_data:
                for var in input_data["variables"]:
                    if var.get("secret"):
                        # Secret variables should not have example values
                        assert "default_value" not in var or var.get("default_value") == "", \
                            f"Secret variable {var['name']} in {name} should have empty default_value"

    def test_framework_presets_structure(self):
        """Test that framework presets have correct structure."""
        preset_keys = ["database", "cache", "auth", "storage", "email", "monitoring", "queue"]
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            if "framework_presets" in input_data:
                for key in preset_keys:
                    # All preset keys should be boolean
                    if key in input_data["framework_presets"]:
                        assert isinstance(input_data["framework_presets"][key], bool), \
                            f"Preset {key} in {name} should be boolean"

    def test_allowed_values_for_enums(self):
        """Test that enum variables have allowed_values."""
        for name, input_data in ENV_EXAMPLE_GENERATOR_INPUTS.items():
            if "variables" in input_data:
                for var in input_data["variables"]:
                    if "allowed_values" in var:
                        assert isinstance(var["allowed_values"], list), \
                            f"allowed_values in {name}.{var['name']} should be list"
                        assert len(var["allowed_values"]) > 0, \
                            f"allowed_values in {name}.{var['name']} should not be empty"
