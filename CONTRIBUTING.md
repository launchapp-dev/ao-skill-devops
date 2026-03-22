# Contributing to ao-skill-devops

Thank you for your interest in contributing to ao-skill-devops! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Making Changes](#making-changes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Skill Pack Development](#skill-pack-development)
- [Release Process](#release-process)
- [Questions and Support](#questions-and-support)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Node.js 18+ or Python 3.11+ (depending on your development focus)
- [AO CLI](https://github.com/launchapp-dev/ao) installed
- Git
- Docker (for testing Dockerfile generation)
- kubectl (for testing Kubernetes manifest generation)
- Access to a Kubernetes cluster (optional, for integration testing)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ao-skill-devops.git
   cd ao-skill-devops
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/launchapp-dev/ao-skill-devops.git
   ```

## Development Setup

### Install Dependencies

```bash
# Install AO CLI if not already installed
npm install -g @launchapp-dev/ao-cli

# Verify installation
ao --version

# Clone and setup
git clone https://github.com/launchapp-dev/ao-skill-devops.git
cd ao-skill-devops
```

### Configure AO for Development

```bash
# Initialize AO in the project directory
ao init

# Verify AO configuration
ao status
```

### Environment Variables

Create a `.env` file for local development:

```bash
# .env file
AO_API_KEY=your_api_key
GITHUB_TOKEN=your_github_token
```

## Project Structure

```
ao-skill-devops/
├── pack.toml           # Skill pack manifest
├── README.md           # Project documentation
├── VISION.md          # Product vision
├── CONTRIBUTING.md    # This file
├── LICENSE            # MIT License
│
├── docs/              # Generator documentation
│   ├── k8s-manifest-generator.md
│   ├── github-actions-generator.md
│   ├── dockerfile-generator.md
│   ├── docker-compose-generator.md
│   ├── railway-config-generator.md
│   ├── vercel-config-generator.md
│   ├── python-ci-generator.md
│   ├── agent-base-framework.md
│   └── integration-testing.md
│
├── skills/            # Skill definitions
│   ├── k8s-manifest-generator.yaml
│   ├── github-actions-generator.yaml
│   ├── dockerfile-generator.yaml
│   ├── docker-compose-generator.yaml
│   ├── railway-config-generator.yaml
│   ├── vercel-config-generator.yaml
│   ├── python-ci-generator.yaml
│   ├── agent-base-framework.yaml
│   ├── integration-tester.yaml
│   ├── railway-config-tester.yaml
│   └── vercel-config-generator-tests.yaml
│
├── workflows/         # Workflow definitions
│   └── skill-pack.yaml
│
├── runtime/           # Runtime configuration
│   └── agents.yaml    # Agent system prompts
│
├── examples/          # Example configurations
│   ├── README.md
│   ├── nodejs/
│   ├── python/
│   ├── go/
│   └── multi-service/
│
└── tests/             # Test suites
    ├── unit/
    ├── integration/
    └── e2e/
```

## Development Workflow

We use a standard GitHub Flow workflow:

1. **Create a branch** from `main` for your changes
2. **Make your changes** following the guidelines
3. **Add tests** for your changes
4. **Update documentation** if needed
5. **Commit your changes** with clear commit messages
6. **Push to your fork**
7. **Create a Pull Request**

### Branch Naming

Use descriptive branch names:

- `feature/add-railway-monorepo-support`
- `fix/dockerfile-healthcheck-timing`
- `docs/improve-k8s-examples`
- `refactor/optimize-layer-caching`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```bash
feat(k8s): add Helm chart generation support
fix(docker): correct multi-stage build order
docs(api): add Railway config examples
test(github-actions): add matrix build tests
```

## Making Changes

### Adding a New Generator

1. **Create the skill definition** in `skills/`:

```yaml
# skills/my-generator.yaml
id: ao.devops/my-generator
description: "Description of what this generator does"
version: "0.1.0"

agent: my-generator-agent

# Input schema
input_schema:
  # ... schema definition

capabilities:
  # ... capabilities

examples:
  basic: |
    input:
      # ... example input
```

2. **Add agent configuration** in `runtime/agents.yaml`:

```yaml
agents:
  my-generator-agent:
    description: "Description"
    system_prompt: |
      # Agent system prompt
    model: kimi-code/kimi-for-coding
    tool: oai-runner
    mcp_servers: ["ao", "context7"]
    capabilities:
      # ... capabilities
```

3. **Add workflow phases** in `workflows/skill-pack.yaml`:

```yaml
phases:
  my-generator-generate:
    mode: agent
    agent: my-generator-agent
    directive: "Generate configuration based on input..."
    capabilities:
      mutates_state: false
    input_schema:
      # ... input schema

workflows:
  - id: ao.devops/my-generator
    name: "My Generator"
    description: "Generate my configuration"
    phases:
      - my-generator-generate
```

4. **Create documentation** in `docs/`:

```markdown
# My Generator

Description...

## Features

- Feature 1
- Feature 2

## Usage

### Example 1

```yaml
input:
  # ... input
```

## Best Practices

1. Practice 1
2. Practice 2
```

5. **Add examples** in `examples/`:

```markdown
# My Generator Example

Example description...

## Input

```yaml
# ... input specification
```

## Generated Output

```yaml
# ... expected output
```
```

6. **Update `pack.toml`** exports:

```toml
[skills]
exports = [
  # ... existing skills
  "ao.devops/my-generator",
]
```

### Modifying Existing Generators

1. Update the skill definition in `skills/`
2. Update agent prompts if needed
3. Update documentation
4. Add or update tests
5. Update examples
6. Update version if breaking changes

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review of your code
- [ ] Comments added for complex logic
- [ ] Tests added for new functionality
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Examples added or updated
- [ ] No breaking changes (or documented)

### PR Description Template

```markdown
## Summary
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

### Review Process

1. Automated checks must pass (linting, tests)
2. At least one maintainer review required
3. Address review feedback
4. Squash and merge when approved

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for generators
└── e2e/           # End-to-end tests
```

### Running Tests

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests
npm run test:integration

# Run specific test file
npm test -- tests/unit/dockerfile-generator.test.ts

# Run with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Writing Tests

```typescript
// tests/unit/my-generator.test.ts
import { describe, it, expect } from 'vitest';
import { MyGenerator } from '../../skills/my-generator';

describe('MyGenerator', () => {
  describe('input validation', () => {
    it('should validate required fields', () => {
      // Test implementation
    });

    it('should reject invalid values', () => {
      // Test implementation
    });
  });

  describe('output generation', () => {
    it('should generate valid output', () => {
      // Test implementation
    });
  });
});
```

### Test Coverage Requirements

- New features must have >80% coverage
- Bug fixes should include regression tests
- Integration tests for each generator

## Documentation

### Updating Documentation

When making changes, update the relevant documentation:

1. **README.md**: Project-level changes
2. **docs/*.md**: Generator-specific documentation
3. **examples/**: Example configurations
4. **VISION.md**: Product vision changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add warnings for common pitfalls
- Keep examples realistic
- Link related documentation

### Generating Documentation

```bash
# Generate API documentation
npm run docs:api

# Generate coverage report
npm run docs:coverage
```

## Skill Pack Development

### Understanding the Pack Structure

The skill pack consists of:

1. **Manifest** (`pack.toml`): Package metadata and exports
2. **Skills** (`skills/`): Individual skill definitions
3. **Workflows** (`workflows/`): Phase and workflow definitions
4. **Runtime** (`runtime/`): Agent configurations
5. **Documentation** (`docs/`): Generator documentation
6. **Examples** (`examples/`): Usage examples

### Skill Definition Schema

Each skill follows this structure:

```yaml
id: ao.devops/[skill-name]
description: "What this skill does"
version: "0.1.0"

agent: [agent-name]

input_schema:
  field_name:
    type: string
    enum: [option1, option2]
    description: Field description
    required: true
    default: default_value

capabilities:
  capability_name: true

examples:
  example_name: |
    input:
      # example input
```

### Agent Prompt Guidelines

System prompts should be:

1. **Clear** about the agent's role and expertise
2. **Comprehensive** about capabilities
3. **Actionable** with step-by-step workflows
4. **Specific** about input/output formats
5. **Quality-focused** with validation rules

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. [ ] Update version in `pack.toml`
2. [ ] Update CHANGELOG.md
3. [ ] Create release PR
4. [ ] Merge release PR
5. [ ] Create GitHub release
6. [ ] Tag with version

### Changelog Format

```markdown
## [0.2.0] - YYYY-MM-DD

### Added
- Feature A
- Feature B

### Changed
- Improvement to X

### Fixed
- Bug in Y

### Deprecated
- Feature Z (will be removed in 0.3.0)

### Removed
- Old deprecated feature
```

## Questions and Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community support
- **Documentation**: Check the [docs/](docs/) directory

## Recognition

Contributors will be recognized in:
- The project's README.md contributors section
- GitHub's contributor graph
- Release notes for significant contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
