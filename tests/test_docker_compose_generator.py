"""
Tests for docker-compose-generator skill and fixtures.

These tests validate the Docker Compose generator fixtures, test scenarios, and
ensure all test categories are properly configured for multi-service orchestration,
networks, volumes, secrets, and health checks.
"""

import os
import pytest
import yaml
from conftest import (
    MockFileSystem,
    TempProjectDir,
    validate_docker_compose,
    assert_valid_output_format,
    DOCKER_COMPOSE_GENERATOR_INPUTS,
)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestDockerComposeGeneratorInputs:
    """Tests for Docker Compose generator input fixtures."""

    def test_basic_input(self):
        """Test basic Docker Compose input fixture."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["basic"]
        assert input_data["compose_version"] == "3.8"
        assert len(input_data["services"]) == 1
        assert input_data["services"][0]["name"] == "web"
        assert input_data["services"][0]["image"] == "nginx:alpine"
        assert "ports" in input_data["services"][0]
        assert "volumes" in input_data["services"][0]
        assert "healthcheck" in input_data["services"][0]
        assert input_data["services"][0]["restart"] == "unless-stopped"

    def test_with_db_input(self):
        """Test Docker Compose input with database fixture."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]
        assert input_data["compose_version"] == "3.8"
        assert len(input_data["services"]) == 3

        # Check API service
        api_service = input_data["services"][0]
        assert api_service["name"] == "api"
        assert "build" in api_service
        assert "ports" in api_service
        assert "environment" in api_service
        assert "depends_on" in api_service
        assert "db" in api_service["depends_on"]
        assert "redis" in api_service["depends_on"]
        assert "healthcheck" in api_service
        assert api_service["restart"] == "unless-stopped"

        # Check DB service
        db_service = input_data["services"][1]
        assert db_service["name"] == "db"
        assert db_service["image"] == "postgres:15-alpine"
        assert "environment" in db_service
        assert "volumes" in db_service
        assert "healthcheck" in db_service
        assert "pg_isready" in str(db_service["healthcheck"]["test"])

        # Check Redis service
        redis_service = input_data["services"][2]
        assert redis_service["name"] == "redis"
        assert redis_service["image"] == "redis:7-alpine"
        assert "healthcheck" in redis_service
        assert "redis-cli" in str(redis_service["healthcheck"]["test"])

        # Check networks
        assert "networks" in input_data
        assert len(input_data["networks"]) == 1
        assert input_data["networks"][0]["name"] == "backend"
        assert input_data["networks"][0]["driver"] == "bridge"

        # Check volumes
        assert "volumes" in input_data
        assert len(input_data["volumes"]) == 2
        assert input_data["volumes"][0]["name"] == "db_data"
        assert input_data["volumes"][1]["name"] == "redis_data"

    def test_dev_stack_input(self):
        """Test Docker Compose development stack fixture."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["dev_stack"]
        assert input_data["compose_version"] == "3.8"
        assert len(input_data["services"]) == 3

        # Check app service has development features
        app_service = input_data["services"][0]
        assert app_service["name"] == "app"
        assert "build" in app_service
        assert app_service["tty"] is True
        assert app_service["stdin_open"] is True
        assert ".:/app" in app_service["volumes"]
        assert "debug" in str(app_service["environment"]).lower()

        # Check ports are exposed for development
        assert "3000:3000" in app_service["ports"]
        assert "9229:9229" in app_service["ports"]

        # Check db service ports
        db_service = input_data["services"][1]
        assert db_service["name"] == "db"
        assert "5432:5432" in db_service["ports"]

        # Check redis service ports
        redis_service = input_data["services"][2]
        assert redis_service["name"] == "redis"
        assert "6379:6379" in redis_service["ports"]

    def test_with_secrets_input(self):
        """Test Docker Compose input with secrets fixture."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]
        assert input_data["compose_version"] == "3.8"
        assert len(input_data["services"]) == 1

        # Check API service with secrets
        api_service = input_data["services"][0]
        assert api_service["name"] == "api"
        assert "secrets" in api_service
        assert "db_password" in api_service["secrets"]
        assert "api_key" in api_service["secrets"]
        assert "depends_on" in api_service
        assert isinstance(api_service["depends_on"], dict)

        # Check conditional depends_on
        depends_on = api_service["depends_on"]
        assert depends_on["db"]["condition"] == "service_healthy"
        assert depends_on["redis"]["condition"] == "service_started"

        # Check healthcheck with start_period
        assert "healthcheck" in api_service
        assert "start_period" in api_service["healthcheck"]

        # Check logging configuration
        assert "logging" in api_service
        assert api_service["logging"]["driver"] == "json-file"
        assert "max-size" in api_service["logging"]["options"]

        # Check secrets definition
        assert "secrets" in input_data
        assert len(input_data["secrets"]) == 2
        assert input_data["secrets"][0]["name"] == "db_password"
        assert input_data["secrets"][0]["file"] == "./secrets/db_password.txt"

        # Check networks
        assert "networks" in input_data
        assert input_data["networks"][0]["name"] == "production"


class TestDockerComposeGeneratorSkill:
    """Tests for docker-compose-generator skill file."""

    def test_skill_file_loads(self):
        """Test that the skill file loads without errors."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        assert skill_data is not None
        assert skill_data["id"] == "ao.devops/docker-compose-generator"
        assert skill_data["version"] == "0.1.0"
        assert skill_data["agent"] == "docker-compose-agent"

    def test_skill_has_capabilities(self):
        """Test that skill has all required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        capabilities = skill_data["capabilities"]
        assert capabilities["docker_compose_generation"] is True
        assert capabilities["multi_service_support"] is True
        assert capabilities["network_configuration"] is True
        assert capabilities["volume_mounts"] is True
        assert capabilities["healthcheck_support"] is True
        assert capabilities["depends_on_support"] is True
        assert capabilities["secrets_support"] is True
        assert capabilities["configs_support"] is True
        assert capabilities["logging_configuration"] is True
        assert capabilities["restart_policy_support"] is True

    def test_skill_has_features(self):
        """Test that skill has all required features."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        features = skill_data["features"]
        assert "multi_service_orchestration" in features
        assert "network_configuration" in features
        assert "volume_mounts" in features
        assert "environment_variables" in features
        assert "health_checks" in features
        assert "depends_on_dependencies" in features
        assert "port_mapping" in features
        assert "restart_policies" in features
        assert "logging_configuration" in features
        assert "secrets_management" in features

    def test_skill_has_input_schema(self):
        """Test that skill has input schema defined."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        schema = skill_data["input_schema"]

        # Check top-level required fields
        assert "compose_version" in schema
        assert "services" in schema
        assert schema["services"]["required"] is True

        # Check service schema has all required properties
        service_props = schema["services"]["items"]["properties"]
        assert "name" in service_props
        assert "image" in service_props
        assert "build" in service_props
        assert "ports" in service_props
        assert "environment" in service_props
        assert "volumes" in service_props
        assert "networks" in service_props
        assert "depends_on" in service_props
        assert "healthcheck" in service_props
        assert "restart" in service_props

        # Check networks schema
        assert "networks" in schema

        # Check volumes schema
        assert "volumes" in schema

        # Check secrets schema
        assert "secrets" in schema

        # Check configs schema
        assert "configs" in schema

    def test_skill_has_examples(self):
        """Test that skill has example inputs."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        examples = skill_data["examples"]
        assert "basic_web_app" in examples
        assert "multi_service_with_db" in examples
        assert "development_stack" in examples
        assert "production_with_secrets" in examples
        assert "with_custom_networks" in examples

    def test_compose_versions_supported(self):
        """Test that skill defines supported compose versions."""
        with open(os.path.join(PROJECT_ROOT, "skills", "docker-compose-generator.yaml"), "r") as f:
            skill_data = yaml.safe_load(f)
        versions = skill_data["compose_versions"]
        assert "3.8" in versions
        assert "3.9" in versions


class TestDockerComposeValidation:
    """Tests for Docker Compose YAML validation."""

    def test_validate_basic_compose(self):
        """Test validation of basic docker-compose structure."""
        compose_content = """
version: "3.8"
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    healthcheck:
      test: "curl -f http://localhost/ || exit 1"
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_multi_service_compose(self):
        """Test validation of multi-service docker-compose structure."""
        compose_content = """
version: "3.8"
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      DATABASE_URL: postgres://postgres:secret@db:5432/myapp
    depends_on:
      - db
      - redis
    healthcheck:
      test: "curl -f http://localhost:3000/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
networks:
  backend:
    driver: bridge
volumes:
  db_data:
  redis_data:
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_with_secrets(self):
        """Test validation of docker-compose with secrets."""
        compose_content = """
version: "3.8"
services:
  api:
    image: myregistry/myapp:v1.0.0
    ports:
      - "8080:8080"
    secrets:
      - db_password
      - api_key
    environment:
      NODE_ENV: production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: "curl -f http://localhost:8080/health || exit 1"
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "3"
secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
networks:
  production:
    driver: bridge
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_with_networks(self):
        """Test validation of docker-compose with custom networks."""
        compose_content = """
version: "3.8"
services:
  frontend:
    image: nginx:alpine
    networks:
      - web
  api:
    build: ./api
    networks:
      - web
      - backend
  db:
    image: postgres:15-alpine
    networks:
      - backend
networks:
  web:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
  backend:
    driver: bridge
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_with_volumes(self):
        """Test validation of docker-compose with volumes."""
        compose_content = """
version: "3.8"
services:
  db:
    image: postgres:15-alpine
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      - /tmp/redis:/tmp/redis:rw
volumes:
  db_data:
    driver: local
  redis_data:
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_with_configs(self):
        """Test validation of docker-compose with configs."""
        compose_content = """
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    ports:
      - "80:80"
configs:
  nginx_config:
    file: ./config/nginx.conf
"""
        assert validate_docker_compose(compose_content) is True

    def test_validate_development_stack(self):
        """Test validation of development stack docker-compose."""
        compose_content = """
version: "3.8"
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
      - "9229:9229"
    environment:
      NODE_ENV: development
      DEBUG: "true"
    volumes:
      - ".:/app"
      - "/app/node_modules"
    tty: true
    stdin_open: true
    depends_on:
      - db
      - redis
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: devdb
    volumes:
      - pg_data:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
networks:
  dev:
    driver: bridge
volumes:
  pg_data:
  redis_data:
"""
        assert validate_docker_compose(compose_content) is True


class TestDockerComposeFixtures:
    """Tests for Docker Compose-specific fixtures."""

    def test_all_compose_inputs_have_required_fields(self):
        """Test that all Docker Compose inputs have required fields."""
        required_fields = ["compose_version", "services"]
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            for field in required_fields:
                assert field in input_data, f"Missing {field} in {name}"

    def test_all_services_have_name(self):
        """Test that all services have a name."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            for service in input_data["services"]:
                assert "name" in service, f"Missing name in {name} service"
                assert isinstance(service["name"], str), f"Invalid name type in {name}"

    def test_healthcheck_fixtures_have_required_fields(self):
        """Test that healthcheck fixtures have required fields."""
        required_fields = ["test", "interval", "timeout", "retries"]
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            for service in input_data["services"]:
                if "healthcheck" in service and service["healthcheck"] is not None:
                    for field in required_fields:
                        assert field in service["healthcheck"], f"Missing {field} in {name} healthcheck"

    def test_secrets_fixture_structure(self):
        """Test that secrets fixture has proper structure."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Check service has secrets
        api_service = input_data["services"][0]
        assert "secrets" in api_service
        assert len(api_service["secrets"]) == 2

        # Check secrets definition exists
        assert "secrets" in input_data
        assert len(input_data["secrets"]) == 2

        # Check each secret has required fields
        for secret in input_data["secrets"]:
            assert "name" in secret
            assert "file" in secret

    def test_network_fixture_structure(self):
        """Test that network fixtures have proper structure."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            if "networks" in input_data:
                for network in input_data["networks"]:
                    assert "name" in network, f"Missing name in {name} network"
                    assert "driver" in network, f"Missing driver in {name} network"

    def test_volume_fixture_structure(self):
        """Test that volume fixtures have proper structure."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            if "volumes" in input_data:
                for volume in input_data["volumes"]:
                    assert "name" in volume, f"Missing name in {name} volume"
                    assert "driver" in volume, f"Missing driver in {name} volume"

    def test_depends_on_fixture_structure(self):
        """Test that depends_on fixtures have proper structure."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service with depends_on
        api_service = input_data["services"][0]
        assert "depends_on" in api_service
        assert isinstance(api_service["depends_on"], list)
        assert "db" in api_service["depends_on"]
        assert "redis" in api_service["depends_on"]

    def test_conditional_depends_on_fixture_structure(self):
        """Test that conditional depends_on fixtures have proper structure."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Find API service with conditional depends_on
        api_service = input_data["services"][0]
        assert "depends_on" in api_service
        assert isinstance(api_service["depends_on"], dict)

        # Check conditions
        depends_on = api_service["depends_on"]
        assert "db" in depends_on
        assert depends_on["db"]["condition"] == "service_healthy"
        assert "redis" in depends_on
        assert depends_on["redis"]["condition"] == "service_started"

    def test_logging_fixture_structure(self):
        """Test that logging fixtures have proper structure."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Find API service with logging
        api_service = input_data["services"][0]
        assert "logging" in api_service
        assert "driver" in api_service["logging"]
        assert "options" in api_service["logging"]
        assert api_service["logging"]["driver"] == "json-file"

    def test_dev_stack_has_tty_stdin_open(self):
        """Test that dev stack has tty and stdin_open enabled."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["dev_stack"]

        # Find app service
        app_service = input_data["services"][0]
        assert app_service["name"] == "app"
        assert app_service["tty"] is True
        assert app_service["stdin_open"] is True

    def test_basic_compose_uses_nginx(self):
        """Test that basic compose uses nginx image."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["basic"]
        assert input_data["services"][0]["image"] == "nginx:alpine"


class TestDockerComposeAgentExists:
    """Tests for docker-compose-agent in agents.yaml."""

    def test_docker_compose_agent_exists(self):
        """Test that docker-compose-agent is defined in agents.yaml."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        assert "agents" in agents_data
        assert "docker-compose-agent" in agents_data["agents"]

    def test_docker_compose_agent_has_description(self):
        """Test that docker-compose-agent has a description."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["docker-compose-agent"]
        assert "description" in agent
        assert "docker-compose" in agent["description"].lower()

    def test_docker_compose_agent_has_capabilities(self):
        """Test that docker-compose-agent has required capabilities."""
        with open(os.path.join(PROJECT_ROOT, "runtime", "agents.yaml"), "r") as f:
            agents_data = yaml.safe_load(f)
        agent = agents_data["agents"]["docker-compose-agent"]
        capabilities = agent["capabilities"]
        assert capabilities["docker_compose_generation"] is True
        assert capabilities["multi_service_support"] is True
        assert capabilities["network_configuration"] is True
        assert capabilities["volume_mounts"] is True
        assert capabilities["healthcheck_support"] is True


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

    def test_docker_compose_generator_exported(self):
        """Test that docker-compose-generator is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/docker-compose-generator" in pack_data["skills"]["exports"]

    def test_docker_compose_workflow_exported(self):
        """Test that docker-compose workflow is exported in pack.toml."""
        import tomllib
        with open(os.path.join(PROJECT_ROOT, "pack.toml"), "rb") as f:
            pack_data = tomllib.load(f)
        assert "ao.devops/docker-compose" in pack_data["workflows"]["exports"]


class TestMultiServiceOrchestration:
    """Tests for multi-service orchestration in Docker Compose."""

    def test_multiple_services_defined(self):
        """Test that multi-service inputs define multiple services."""
        # Check multi-service fixtures
        multi_service_names = ["with_db", "dev_stack"]
        for name in multi_service_names:
            input_data = DOCKER_COMPOSE_GENERATOR_INPUTS[name]
            assert len(input_data["services"]) >= 2, f"{name} should have multiple services"

    def test_service_dependencies(self):
        """Test that services can define dependencies."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service
        api_service = input_data["services"][0]
        assert "depends_on" in api_service

        # Find dependent services
        depends_on_list = input_data["services"][0]["depends_on"]
        service_names = [s["name"] for s in input_data["services"]]

        for dep in depends_on_list:
            assert dep in service_names, f"Dependency {dep} should be a valid service"

    def test_service_with_build_context(self):
        """Test that services can have build context."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service with build
        api_service = input_data["services"][0]
        assert "build" in api_service
        assert "context" in api_service["build"]
        assert "dockerfile" in api_service["build"]

    def test_service_with_environment(self):
        """Test that services can have environment variables."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service with environment
        api_service = input_data["services"][0]
        assert "environment" in api_service
        assert isinstance(api_service["environment"], dict)

    def test_service_with_ports(self):
        """Test that services can expose ports."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Check API service ports
        api_service = input_data["services"][0]
        assert "ports" in api_service
        assert len(api_service["ports"]) > 0


class TestNetworkConfiguration:
    """Tests for network configuration in Docker Compose."""

    def test_custom_networks_defined(self):
        """Test that custom networks can be defined."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        assert "networks" in input_data
        assert len(input_data["networks"]) > 0

        # Check network structure
        network = input_data["networks"][0]
        assert "name" in network
        assert "driver" in network

    def test_network_driver_types(self):
        """Test that different network drivers can be specified."""
        # All fixtures should use bridge driver
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            if "networks" in input_data:
                for network in input_data["networks"]:
                    assert network["driver"] in ["bridge", "host", "overlay", "none"]

    def test_services_can_join_networks(self):
        """Test that services can be assigned to networks."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Services should be able to reference networks
        # In compose, services reference networks by name in the networks list
        assert "networks" in input_data


class TestVolumeMounts:
    """Tests for volume mounts in Docker Compose."""

    def test_volumes_defined(self):
        """Test that volumes can be defined."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        assert "volumes" in input_data
        assert len(input_data["volumes"]) > 0

        # Check volume structure
        volume = input_data["volumes"][0]
        assert "name" in volume
        assert "driver" in volume

    def test_volume_driver_types(self):
        """Test that different volume drivers can be specified."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            if "volumes" in input_data:
                for volume in input_data["volumes"]:
                    assert "driver" in volume

    def test_services_can_mount_volumes(self):
        """Test that services can mount volumes."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find DB service with volume mount
        db_service = input_data["services"][1]
        assert "volumes" in db_service
        assert len(db_service["volumes"]) > 0

        # Check volume mount format (should reference a named volume)
        for vol in db_service["volumes"]:
            # Should be either named volume or bind mount
            assert ":" in vol or not vol.startswith("/")


class TestSecretsManagement:
    """Tests for secrets management in Docker Compose."""

    def test_secrets_can_be_defined(self):
        """Test that secrets can be defined at top level."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        assert "secrets" in input_data
        assert len(input_data["secrets"]) > 0

        # Check secret structure
        secret = input_data["secrets"][0]
        assert "name" in secret
        assert "file" in secret

    def test_services_can_reference_secrets(self):
        """Test that services can reference secrets."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Find API service with secrets
        api_service = input_data["services"][0]
        assert "secrets" in api_service

        # Check secrets are referenced
        service_secrets = api_service["secrets"]
        defined_secrets = [s["name"] for s in input_data["secrets"]]

        for secret_ref in service_secrets:
            assert secret_ref in defined_secrets

    def test_secrets_have_file_paths(self):
        """Test that secrets specify file paths."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        for secret in input_data["secrets"]:
            assert "file" in secret
            assert secret["file"].startswith("./")


class TestHealthChecks:
    """Tests for health checks in Docker Compose."""

    def test_healthcheck_format_string(self):
        """Test healthcheck with string test format."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["basic"]

        web_service = input_data["services"][0]
        assert "healthcheck" in web_service
        assert isinstance(web_service["healthcheck"]["test"], str)

    def test_healthcheck_format_array(self):
        """Test healthcheck with array test format."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find service with array healthcheck
        for service in input_data["services"]:
            if "pg_isready" in str(service.get("healthcheck", {}).get("test", "")):
                assert isinstance(service["healthcheck"]["test"], list)
                assert service["healthcheck"]["test"][0] == "CMD"

    def test_healthcheck_timing(self):
        """Test healthcheck timing parameters."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service with healthcheck
        api_service = input_data["services"][0]
        healthcheck = api_service["healthcheck"]

        assert "interval" in healthcheck
        assert "timeout" in healthcheck
        assert "retries" in healthcheck
        assert "start_period" in healthcheck

    def test_healthcheck_retries_count(self):
        """Test healthcheck retry counts."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            for service in input_data["services"]:
                if "healthcheck" in service:
                    retries = service["healthcheck"]["retries"]
                    assert isinstance(retries, int)
                    assert retries > 0

    def test_multiple_healthcheck_commands(self):
        """Test different healthcheck command types."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        healthcheck_commands = []
        for service in input_data["services"]:
            if "healthcheck" in service:
                test = service["healthcheck"]["test"]
                if isinstance(test, list):
                    healthcheck_commands.append(" ".join(test))
                else:
                    healthcheck_commands.append(test)

        # Should have different types of healthcheck commands
        assert len(healthcheck_commands) >= 2


class TestRestartPolicies:
    """Tests for restart policies in Docker Compose."""

    def test_restart_policy_values(self):
        """Test that restart policies use valid values."""
        valid_policies = ["no", "always", "on-failure", "unless-stopped"]

        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            for service in input_data["services"]:
                if "restart" in service:
                    assert service["restart"] in valid_policies

    def test_restart_policy_for_api_service(self):
        """Test restart policy for API service."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_db"]

        # Find API service
        api_service = input_data["services"][0]
        assert api_service["restart"] == "unless-stopped"


class TestLoggingConfiguration:
    """Tests for logging configuration in Docker Compose."""

    def test_logging_driver(self):
        """Test logging driver configuration."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Find API service with logging
        api_service = input_data["services"][0]
        assert "logging" in api_service
        assert api_service["logging"]["driver"] == "json-file"

    def test_logging_options(self):
        """Test logging driver options."""
        input_data = DOCKER_COMPOSE_GENERATOR_INPUTS["with_secrets"]

        # Find API service with logging
        api_service = input_data["services"][0]
        logging_config = api_service["logging"]

        assert "options" in logging_config
        assert "max-size" in logging_config["options"]
        assert "max-file" in logging_config["options"]


class TestComposeVersion:
    """Tests for Docker Compose version."""

    def test_compose_version_values(self):
        """Test that compose versions are valid."""
        valid_versions = ["3.8", "3.9", "3.7", "3.3"]

        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            assert "compose_version" in input_data
            assert input_data["compose_version"] in valid_versions

    def test_compose_version_38_recommended(self):
        """Test that 3.8 is the recommended compose version."""
        for name, input_data in DOCKER_COMPOSE_GENERATOR_INPUTS.items():
            assert input_data["compose_version"] == "3.8"
