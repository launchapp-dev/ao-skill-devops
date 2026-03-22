# Agent Base Framework

Base classes and utilities for all DevOps config generators in the ao-skill-devops pack.

## Overview

The Agent Base Framework provides foundational components that all DevOps generator agents depend on. It ensures consistency, maintainability, and best practices across all generated configuration code.

## Components

### Agent Base Class

The base class for all DevOps generator agents, providing common patterns for file generation, validation, and output formatting.

**Features:**
- Common methods: file generation, validation, error handling
- Logging integration with structured output
- Schema validation support
- Output formatting utilities
- Support for TypeScript and Python implementations

### PromptBuilder

Utility for building structured prompts from templates and input specifications.

**Features:**
- Template-based prompt construction
- Variable substitution and context injection
- Multi-section prompt support
- Format preservation across sections
- Template caching and partial rendering
- Custom filter support

### TemplateRenderer

Renders configuration templates with variable substitution and validation.

**Features:**
- Jinja2-style template engine
- Schema-validated output
- Partial template rendering
- Custom filters (k8s_name, docker_tag, env_var, etc.)
- Include/extend support
- Whitespace control
- Loop and conditional support

### ValidationHelpers

Common validation utilities for generated configs.

**Features:**
- YAML schema validation
- JSON schema validation
- Kubernetes manifest validation
- Dockerfile syntax validation
- GitHub Actions workflow validation
- Best practices checking
- Error reporting with line numbers

## Usage

### Generate Base Framework Components

```yaml
agent: agent-base-framework-agent
input:
  component_type: all
  target_language: typescript
  options:
    include_validation: true
    include_logging: true
```

### Generate Specific Components

**Agent Base Class:**
```yaml
agent: agent-base-framework-agent
input:
  component_type: agent_base
  target_language: typescript
  options:
    include_validation: true
    include_logging: true
```

**PromptBuilder:**
```yaml
agent: agent-base-framework-agent
input:
  component_type: prompt_builder
  target_language: typescript
  options:
    template_engine: jinja2
    include_context: true
```

**TemplateRenderer:**
```yaml
agent: agent-base-framework-agent
input:
  component_type: template_renderer
  target_language: python
  options:
    filters:
      - k8s_name
      - docker_tag
    partials: true
```

**ValidationHelpers:**
```yaml
agent: agent-base-framework-agent
input:
  component_type: validation_helpers
  target_language: typescript
  options:
    schemas:
      - kubernetes
      - dockerfile
      - github_actions
```

## Supported Languages

- **TypeScript**: Full support with interfaces and type definitions
- **Python**: Full support with type hints and dataclasses
- **Bash**: Basic support for shell scripts

## Dependencies

The agent-base-framework is a foundational component that other DevOps skills depend on:

- `ao.devops/k8s-manifest-generator` - Uses framework for manifest generation
- `ao.devops/integration-tester` - Uses framework for test utilities

## Code Quality Standards

All generated framework code follows these standards:

- **Clean, well-structured code**: Proper organization and separation of concerns
- **Naming conventions**: PascalCase for classes, camelCase for methods, SCREAMING_SNAKE_CASE for constants
- **Comprehensive documentation**: JSDoc/docstrings for all public APIs
- **Error handling**: Proper try/catch blocks and error propagation
- **SOLID principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Testability**: Code designed for easy mocking and testing

## Workflow Integration

The base framework can be generated and tested using the following workflow:

```
agent-base-framework-generate → integration-test → push-branch → create-pr → pr-review
```

## License

MIT
