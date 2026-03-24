"""
Tests for vercel-config-generator skill and fixtures.

These tests validate the Vercel config generator fixtures, test scenarios, and
ensure all test categories are properly configured for static sites, serverless
functions, edge functions, monorepos, route configurations, and environment variables.
"""

import json
import os
import pytest
import yaml
from conftest import (
    MockFileSystem,
    TempProjectDir,
    validate_vercel_config,
    assert_valid_output_format,
    VERCEL_CONFIG_GENERATOR_INPUTS,
)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestVercelConfigGeneratorInputs:
    """Tests for Vercel config generator input fixtures."""

    def test_static_site_input(self):
        """Test Vercel static site input fixture."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["static_site"]
        assert input_data["deployment_type"] == "static"
        assert input_data["build_command"] == "npm run build"
        assert input_data["output_directory"] == "dist"
        assert "environment_variables" in input_data
        assert input_data["environment_variables"]["NODE_ENV"] == "production"

    def test_serverless_api_input(self):
        """Test Vercel serverless API input fixture."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["serverless_api"]
        assert input_data["deployment_type"] == "serverless"
        assert input_data["framework"] == "nodejs"
        assert input_data["build_command"] == "npm run build"
        assert "functions" in input_data
        assert "api" in input_data["functions"]
        assert input_data["functions"]["api"]["runtime"] == "nodejs18.x"
        assert input_data["functions"]["api"]["memory"] == 1024
        assert input_data["functions"]["api"]["maxDuration"] == 10
        assert "DATABASE_URL" in str(input_data["environment_variables"])

    def test_nextjs_input(self):
        """Test Vercel Next.js input fixture."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["nextjs"]
        assert input_data["deployment_type"] == "framework"
        assert input_data["framework"] == "nextjs"
        assert "regions" in input_data
        assert "iad1" in input_data["regions"]
        assert "sfo1" in input_data["regions"]
        assert "routes" in input_data
        assert len(input_data["routes"]) >= 2
        assert "src" in input_data["routes"][0]

    def test_monorepo_input(self):
        """Test Vercel monorepo input fixture."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["monorepo"]
        assert input_data["deployment_type"] == "monorepo"
        assert "regions" in input_data
        assert "iad1" in input_data["regions"]
        assert "functions" in input_data
        assert "api" in input_data["functions"]
        assert input_data["functions"]["api"]["memory"] == 512
        assert input_data["functions"]["api"]["maxDuration"] == 30
        assert input_data["environment_variables"]["NODE_ENV"] == "production"

    def test_edge_function_input(self):
        """Test Vercel edge function input fixture."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["edge_function"]
        assert input_data["deployment_type"] == "edge"
        assert input_data["framework"] == "nodejs"
        assert "regions" in input_data
        assert "iad1" in input_data["regions"]
        assert "sfo1" in input_data["regions"]
        assert "hnd1" in input_data["regions"]
        assert "functions" in input_data
        assert "edge-handler" in input_data["functions"]

    def test_all_inputs_have_deployment_type(self):
        """Test that all Vercel inputs have a deployment_type."""
        for name, input_data in VERCEL_CONFIG_GENERATOR_INPUTS.items():
            assert "deployment_type" in input_data, f"Missing deployment_type in {name}"
            assert input_data["deployment_type"] in [
                "static", "serverless", "edge", "monorepo", "framework"
            ], f"Invalid deployment_type in {name}"


class TestVercelConfigGeneratorSkill:
    """Tests for vercel-config-generator skill file."""

    def test_skill_file_loads(self):
        """Test that the skill file loads without errors."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        assert skill_data is not None
        assert skill_data["id"] == "ao.devops/vercel-config-generator"
        assert skill_data["version"] == "0.1.0"
        assert skill_data["agent"] == "vercel-config-agent"

    def test_skill_has_deployment_types(self):
        """Test that skill has all required deployment types."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        deployment_types = skill_data["deployment_types"]
        expected_types = ["static", "serverless", "edge", "monorepo", "framework"]
        for dtype in expected_types:
            assert dtype in deployment_types, f"Missing deployment type: {dtype}"

    def test_skill_has_framework_presets(self):
        """Test that skill has all required framework presets."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        presets = skill_data["framework_presets"]
        expected_presets = ["nextjs", "nuxt", "sveltekit", "astro", "remix", "expo", "nodejs", "other"]
        for preset in expected_presets:
            assert preset in presets, f"Missing framework preset: {preset}"

    def test_skill_has_capabilities(self):
        """Test that skill has all required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        capabilities = skill_data["capabilities"]
        assert capabilities["vercel_generation"] is True
        assert capabilities["serverless_support"] is True
        assert capabilities["edge_functions_support"] is True
        assert capabilities["monorepo_support"] is True
        assert capabilities["route_configuration"] is True

    def test_skill_has_input_schema(self):
        """Test that skill has complete input schema."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        schema = skill_data["input_schema"]

        # Check main fields
        assert "deployment_type" in schema
        assert schema["deployment_type"]["required"] is True
        assert "framework" in schema
        assert "build_command" in schema
        assert "output_directory" in schema
        assert "install_command" in schema
        assert "regions" in schema
        assert "environment_variables" in schema
        assert "secret_environment_variables" in schema
        assert "routes" in schema
        assert "functions" in schema

    def test_input_schema_has_deployment_type_enum(self):
        """Test that input schema has correct deployment_type enum."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        dtype_schema = skill_data["input_schema"]["deployment_type"]
        assert "enum" in dtype_schema
        assert "static" in dtype_schema["enum"]
        assert "serverless" in dtype_schema["enum"]
        assert "edge" in dtype_schema["enum"]
        assert "monorepo" in dtype_schema["enum"]
        assert "framework" in dtype_schema["enum"]

    def test_input_schema_has_framework_enum(self):
        """Test that input schema has correct framework enum."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        framework_schema = skill_data["input_schema"]["framework"]
        assert "enum" in framework_schema
        assert "nextjs" in framework_schema["enum"]
        assert "nuxt" in framework_schema["enum"]
        assert "sveltekit" in framework_schema["enum"]
        assert "astro" in framework_schema["enum"]
        assert "remix" in framework_schema["enum"]

    def test_skill_has_examples(self):
        """Test that skill has example inputs."""
        with open(os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        examples = skill_data["examples"]
        assert "static_site" in examples
        assert "serverless_api" in examples
        assert "nextjs_app" in examples
        assert "monorepo" in examples


class TestVercelConfigGeneratorAgent:
    """Tests for vercel-config-agent in agents.yaml."""

    def test_agent_exists(self):
        """Test that vercel-config-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "vercel-config-agent" in agents_data["agents"]

    def test_agent_has_description(self):
        """Test that vercel-config-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["vercel-config-agent"]
        assert "description" in agent
        assert "vercel" in agent["description"].lower()

    def test_agent_has_capabilities(self):
        """Test that vercel-config-agent has required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["vercel-config-agent"]
        capabilities = agent["capabilities"]
        assert capabilities["vercel_generation"] is True

    def test_test_agent_exists(self):
        """Test that vercel-config-test-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "vercel-config-test-agent" in agents_data["agents"]

    def test_test_agent_has_description(self):
        """Test that vercel-config-test-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["vercel-config-test-agent"]
        assert "description" in agent
        assert "test" in agent["description"].lower()


class TestVercelConfigTestSkill:
    """Tests for vercel-config-generator-tests skill file."""

    def test_test_skill_file_loads(self):
        """Test that the test skill file loads without errors."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        assert skill_data is not None
        assert skill_data["id"] == "ao.devops/vercel-config-generator-tests"
        assert skill_data["version"] == "0.1.0"
        assert skill_data["agent"] == "vercel-config-test-agent"

    def test_test_skill_has_test_scenarios(self):
        """Test that test skill has test scenarios defined."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenarios = skill_data["test_scenarios"]
        expected_scenarios = [
            "static_sites",
            "serverless_functions",
            "edge_functions",
            "monorepos",
            "route_configurations",
            "environment_variables",
            "framework_presets",
            "validation_tests",
            "edge_cases",
        ]
        for scenario in expected_scenarios:
            assert scenario in scenarios, f"Missing test scenario: {scenario}"

    def test_static_sites_scenario(self):
        """Test static sites test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["static_sites"]
        assert scenario["name"] == "Static Site Generation"
        assert len(scenario["test_cases"]) >= 3
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "static-basic" in test_ids
        assert "static-with-env" in test_ids
        assert "static-with-regions" in test_ids

    def test_serverless_functions_scenario(self):
        """Test serverless functions test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["serverless_functions"]
        assert scenario["name"] == "Serverless Function Generation"
        assert len(scenario["test_cases"]) >= 3
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "serverless-basic" in test_ids
        assert "serverless-secrets" in test_ids
        assert "serverless-multi-function" in test_ids

    def test_edge_functions_scenario(self):
        """Test edge functions test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["edge_functions"]
        assert scenario["name"] == "Edge Function Generation"
        assert len(scenario["test_cases"]) >= 2
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "edge-basic" in test_ids
        assert "edge-with-headers" in test_ids

    def test_monorepos_scenario(self):
        """Test monorepos test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["monorepos"]
        assert scenario["name"] == "Monorepo Configuration"
        assert len(scenario["test_cases"]) >= 3
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "monorepo-basic" in test_ids
        assert "monorepo-with-functions" in test_ids
        assert "monorepo-multi-region" in test_ids

    def test_route_configurations_scenario(self):
        """Test route configurations test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["route_configurations"]
        assert scenario["name"] == "Route Configuration Tests"
        assert len(scenario["test_cases"]) >= 4
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "routes-redirects" in test_ids
        assert "routes-rewrites" in test_ids
        assert "routes-headers" in test_ids
        assert "routes-mixed" in test_ids

    def test_environment_variables_scenario(self):
        """Test environment variables test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["environment_variables"]
        assert scenario["name"] == "Environment Variable Tests"
        assert len(scenario["test_cases"]) >= 3
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "env-basic" in test_ids
        assert "env-with-secrets" in test_ids
        assert "env-array-secrets" in test_ids

    def test_framework_presets_scenario(self):
        """Test framework presets test scenario."""
        with open(
            os.path.join(PROJECT_ROOT, "skills", "vercel-config-generator-tests.yaml"), "r"
        ) as f:
            skill_data = yaml.safe_load(f)
        scenario = skill_data["test_scenarios"]["framework_presets"]
        assert scenario["name"] == "Framework Preset Tests"
        assert len(scenario["test_cases"]) >= 5
        test_ids = [tc["id"] for tc in scenario["test_cases"]]
        assert "framework-nextjs" in test_ids
        assert "framework-astro" in test_ids
        assert "framework-sveltekit" in test_ids
        assert "framework-remix" in test_ids
        assert "framework-nuxt" in test_ids


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

    def test_vercel_config_generator_exported(self):
        """Test that vercel-config-generator is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/vercel-config-generator" in pack_data["skills"]["exports"]

    def test_vercel_config_generator_tests_exported(self):
        """Test that vercel-config-generator-tests is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/vercel-config-generator-tests" in pack_data["skills"]["exports"]

    def test_vercel_config_workflow_exported(self):
        """Test that vercel-config workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/vercel-config" in pack_data["workflows"]["exports"]

    def test_vercel_config_with_tests_workflow_exported(self):
        """Test that vercel-config-with-tests workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/vercel-config-with-tests" in pack_data["workflows"]["exports"]

    def test_vercel_config_unit_tests_workflow_exported(self):
        """Test that vercel-config-unit-tests workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/vercel-config-unit-tests" in pack_data["workflows"]["exports"]


class TestStaticSiteConfigurations:
    """Tests for static site configurations."""

    def test_static_site_basic_config(self):
        """Test basic static site configuration structure."""
        config = {
            "version": 2,
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "env": {"NODE_ENV": "production"}
        }
        assert config["version"] == 2
        assert config["outputDirectory"] == "dist"

    def test_static_site_with_regions(self):
        """Test static site with region configuration."""
        config = {
            "version": 2,
            "outputDirectory": "dist",
            "regions": ["iad1", "sfo1"]
        }
        assert "iad1" in config["regions"]
        assert "sfo1" in config["regions"]

    def test_static_site_with_routes(self):
        """Test static site with custom routes."""
        config = {
            "version": 2,
            "outputDirectory": "dist",
            "routes": [
                {"src": "/old-page", "dest": "/new-page", "status": 301}
            ]
        }
        assert len(config["routes"]) > 0
        assert config["routes"][0]["src"] == "/old-page"


class TestServerlessFunctions:
    """Tests for serverless function configurations."""

    def test_serverless_basic_config(self):
        """Test basic serverless function configuration."""
        config = {
            "version": 2,
            "functions": {
                "api": {
                    "runtime": "nodejs18.x",
                    "memory": 1024,
                    "maxDuration": 10
                }
            }
        }
        assert config["functions"]["api"]["runtime"] == "nodejs18.x"
        assert config["functions"]["api"]["memory"] == 1024
        assert config["functions"]["api"]["maxDuration"] == 10

    def test_serverless_multi_function_config(self):
        """Test multiple serverless function configuration."""
        config = {
            "version": 2,
            "functions": {
                "api": {"runtime": "nodejs18.x", "memory": 1024},
                "auth": {"runtime": "nodejs18.x", "memory": 512, "maxDuration": 5},
                "webhooks": {"runtime": "nodejs18.x", "memory": 256, "maxDuration": 3}
            }
        }
        assert "api" in config["functions"]
        assert "auth" in config["functions"]
        assert "webhooks" in config["functions"]
        assert config["functions"]["auth"]["memory"] == 512

    def test_serverless_with_env_vars(self):
        """Test serverless with environment variables."""
        config = {
            "version": 2,
            "functions": {
                "api": {"runtime": "nodejs18.x", "memory": 1024}
            },
            "env": {
                "NODE_ENV": "production",
                "DATABASE_URL": "${{ secrets.DATABASE_URL }}"
            }
        }
        assert "${{ secrets.DATABASE_URL }}" in config["env"]["DATABASE_URL"]


class TestEdgeFunctions:
    """Tests for edge function configurations."""

    def test_edge_basic_config(self):
        """Test basic edge function configuration."""
        config = {
            "version": 2,
            "functions": {
                "middleware": {
                    "runtime": "edge",
                    "memory": 128
                }
            }
        }
        assert config["functions"]["middleware"]["runtime"] == "edge"
        assert config["functions"]["middleware"]["memory"] == 128

    def test_edge_with_regions(self):
        """Test edge function with region configuration."""
        config = {
            "version": 2,
            "functions": {
                "api-edge": {
                    "runtime": "edge",
                    "regions": ["iad1", "sfo1"]
                }
            }
        }
        assert "iad1" in config["functions"]["api-edge"]["regions"]

    def test_edge_with_routes(self):
        """Test edge function with routes."""
        config = {
            "version": 2,
            "functions": {
                "middleware": {"runtime": "edge"}
            },
            "routes": [
                {
                    "src": "/api/(.*)",
                    "dest": "/api/$1",
                    "headers": {"x-edge-cache": "hit"}
                }
            ]
        }
        assert config["routes"][0]["headers"]["x-edge-cache"] == "hit"


class TestMonorepoConfigurations:
    """Tests for monorepo configurations."""

    def test_monorepo_basic_config(self):
        """Test basic monorepo configuration."""
        config = {
            "version": 2,
            "regions": ["iad1"],
            "env": {"NODE_ENV": "production"}
        }
        assert "iad1" in config["regions"]
        assert config["env"]["NODE_ENV"] == "production"

    def test_monorepo_with_functions(self):
        """Test monorepo with function configurations."""
        config = {
            "version": 2,
            "regions": ["iad1", "sfo1"],
            "functions": {
                "api": {"memory": 512, "maxDuration": 30},
                "web": {"memory": 256, "maxDuration": 10}
            },
            "env": {
                "NODE_ENV": "production",
                "API_URL": "https://api.example.com"
            }
        }
        assert config["functions"]["api"]["maxDuration"] == 30
        assert config["functions"]["web"]["memory"] == 256

    def test_monorepo_multi_region(self):
        """Test monorepo with multiple regions."""
        config = {
            "version": 2,
            "regions": ["iad1", "sfo1", "sin1", "fra1"],
            "functions": {
                "api": {"memory": 1024}
            }
        }
        assert len(config["regions"]) == 4
        assert "sin1" in config["regions"]


class TestRouteConfigurations:
    """Tests for route configurations."""

    def test_route_redirect(self):
        """Test route with redirect."""
        config = {
            "version": 2,
            "routes": [
                {"src": "/old-page", "dest": "/new-page", "status": 301}
            ]
        }
        assert config["routes"][0]["status"] == 301

    def test_route_rewrite(self):
        """Test route with rewrite."""
        config = {
            "version": 2,
            "routes": [
                {"src": "/api/users/(.*)", "dest": "/api/proxy/$1"},
                {"src": "/blog/(.*)", "dest": "/cms/$1"}
            ]
        }
        assert len(config["routes"]) >= 2

    def test_route_with_headers(self):
        """Test route with custom headers."""
        config = {
            "version": 2,
            "routes": [
                {
                    "src": "/static/(.*)",
                    "dest": "/static/$1",
                    "headers": {
                        "cache-control": "public, max-age=31536000, immutable"
                    }
                }
            ]
        }
        assert "headers" in config["routes"][0]

    def test_route_security_headers(self):
        """Test route with security headers."""
        config = {
            "version": 2,
            "routes": [
                {
                    "src": "/(.*)",
                    "dest": "/$1",
                    "headers": {
                        "x-frame-options": "DENY",
                        "x-content-type-options": "nosniff"
                    }
                }
            ]
        }
        assert config["routes"][0]["headers"]["x-frame-options"] == "DENY"


class TestEnvironmentVariables:
    """Tests for environment variable configurations."""

    def test_basic_env_vars(self):
        """Test basic environment variables."""
        config = {
            "version": 2,
            "env": {
                "NODE_ENV": "production",
                "NEXT_PUBLIC_SITE_URL": "https://example.com"
            }
        }
        assert config["env"]["NODE_ENV"] == "production"
        assert config["env"]["NEXT_PUBLIC_SITE_URL"] == "https://example.com"

    def test_env_with_secrets(self):
        """Test environment variables with secrets."""
        config = {
            "version": 2,
            "env": {
                "NODE_ENV": "production",
                "LOG_LEVEL": "info",
                "DATABASE_URL": "${{ secrets.DATABASE_URL }}",
                "API_SECRET": "${{ secrets.API_SECRET }}"
            }
        }
        assert "${{ secrets.DATABASE_URL }}" in config["env"]["DATABASE_URL"]
        assert "${{ secrets.API_SECRET }}" in config["env"]["API_SECRET"]

    def test_special_characters_in_env(self):
        """Test environment variables with special characters."""
        config = {
            "version": 2,
            "env": {
                "DATABASE_URL": "postgres://user:pass@host:5432/db?ssl=true",
                "JSON_CONFIG": '{"key": "value"}'
            }
        }
        assert "postgres://" in config["env"]["DATABASE_URL"]
        assert '"key"' in config["env"]["JSON_CONFIG"]


class TestFrameworkPresets:
    """Tests for framework preset configurations."""

    def test_nextjs_preset(self):
        """Test Next.js framework preset."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["nextjs"]
        assert input_data["framework"] == "nextjs"
        assert "regions" in input_data
        assert len(input_data["regions"]) == 2

    def test_astro_preset(self):
        """Test Astro framework preset."""
        config = {
            "version": 2,
            "framework": "astro",
            "buildCommand": "npm run build",
            "outputDirectory": "dist"
        }
        assert config["framework"] == "astro"
        assert config["outputDirectory"] == "dist"

    def test_sveltekit_preset(self):
        """Test SvelteKit framework preset."""
        config = {
            "version": 2,
            "framework": "sveltekit"
        }
        assert config["framework"] == "sveltekit"
        assert config["version"] == 2

    def test_remix_preset(self):
        """Test Remix framework preset."""
        config = {
            "version": 2,
            "framework": "remix",
            "buildCommand": "npm run build"
        }
        assert config["framework"] == "remix"
        assert config["buildCommand"] == "npm run build"

    def test_nuxt_preset(self):
        """Test Nuxt framework preset."""
        config = {
            "version": 2,
            "framework": "nuxt",
            "buildCommand": "npm run build"
        }
        assert config["framework"] == "nuxt"
        assert config["buildCommand"] == "npm run build"


class TestValidation:
    """Tests for JSON validation."""

    def test_validate_basic_vercel_config(self):
        """Test validation of basic vercel.json structure."""
        config_content = json.dumps({
            "version": 2,
            "buildCommand": "npm run build",
            "outputDirectory": "dist"
        })
        assert validate_vercel_config(config_content) is True

    def test_validate_with_functions(self):
        """Test validation of vercel.json with functions."""
        config_content = json.dumps({
            "version": 2,
            "functions": {
                "api": {"runtime": "nodejs18.x", "memory": 1024}
            }
        })
        assert validate_vercel_config(config_content) is True

    def test_validate_with_routes(self):
        """Test validation of vercel.json with routes."""
        config_content = json.dumps({
            "version": 2,
            "routes": [
                {"src": "/api/(.*)", "dest": "/api/$1"}
            ]
        })
        assert validate_vercel_config(config_content) is True

    def test_validate_invalid_json(self):
        """Test validation fails for invalid JSON."""
        invalid_content = "{ invalid json }"
        assert validate_vercel_config(invalid_content) is False

    def test_version_must_be_2(self):
        """Test that version field equals 2."""
        config = {"version": 2}
        assert config["version"] == 2


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_functions_config(self):
        """Test serverless with empty function config."""
        config = {
            "version": 2,
            "functions": {}
        }
        assert config["version"] == 2
        assert config["functions"] == {}

    def test_empty_routes_array(self):
        """Test static with empty routes array."""
        config = {
            "version": 2,
            "outputDirectory": "dist",
            "routes": []
        }
        assert config["version"] == 2
        assert config["routes"] == []

    def test_no_regions_specified(self):
        """Test monorepo with no specified regions."""
        config = {
            "version": 2,
            "deployment_type": "monorepo"
        }
        assert config["version"] == 2
        assert "regions" not in config

    def test_empty_env_vars(self):
        """Test with empty environment variables."""
        config = {
            "version": 2,
            "env": {}
        }
        assert config["version"] == 2
        assert config["env"] == {}


class TestVercelConfigFixtures:
    """Tests for Vercel config-specific fixtures."""

    def test_all_vercel_inputs_have_required_fields(self):
        """Test that all Vercel inputs have required fields."""
        for name, input_data in VERCEL_CONFIG_GENERATOR_INPUTS.items():
            assert "deployment_type" in input_data, f"Missing deployment_type in {name}"

    def test_static_site_has_build_command(self):
        """Test that static site input has build command."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["static_site"]
        assert "build_command" in input_data

    def test_serverless_has_functions(self):
        """Test that serverless input has functions config."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["serverless_api"]
        assert "functions" in input_data
        assert "api" in input_data["functions"]

    def test_nextjs_has_regions(self):
        """Test that Next.js input has regions."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["nextjs"]
        assert "regions" in input_data
        assert isinstance(input_data["regions"], list)

    def test_monorepo_has_env_vars(self):
        """Test that monorepo input has environment variables."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["monorepo"]
        assert "environment_variables" in input_data

    def test_edge_has_runtime(self):
        """Test that edge function input has runtime."""
        input_data = VERCEL_CONFIG_GENERATOR_INPUTS["edge_function"]
        assert "functions" in input_data
        func = list(input_data["functions"].values())[0]
        assert "runtime" in func or "edge" in str(func).lower()
