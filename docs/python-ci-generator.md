# Python CI Generator

A specialized agent for generating GitHub Actions workflows for Python CI with pytest testing and coverage reporting.

## Features

- **Pytest Support**: Configurable pytest test runner with custom arguments
- **Coverage Reporting**: Integration with coverage.py for test coverage analysis
- **Coverage Threshold**: Enforce minimum coverage requirements (default: 80%)
- **Multiple Package Managers**: pip, Poetry, Pipenv, and PDM support
- **Linting Integration**: ruff, pylint, flake8, and black support
- **Dependency Caching**: Optimized build times with pip/poetry/pipenv/pdm caching
- **Matrix Builds**: Test across multiple Python versions simultaneously
- **Codecov Integration**: Optional upload to Codecov for coverage tracking

## Usage

### Direct Agent Invocation

```yaml
agent: python-ci-agent
input:
  environment: python
  name: Python CI
  version: "3.11"
  package_manager: poetry
  coverage_threshold: 80
  fail_under: 80
  lint: true
  linter: ruff
  cache: true
```

### Generated Output

The agent produces a production-ready GitHub Actions workflow:

```yaml
name: Python CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache Poetry dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pypoetry
            ~/.cache/pip
          key: ${{ runner.os }}-poetry-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
          restore-keys: |
            ${{ runner.os }}-poetry-${{ matrix.python-version }}-
            ${{ runner.os }}-poetry-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          poetry install

      - name: Lint with ruff
        run: poetry run ruff check .

      - name: Run tests with coverage
        run: |
          poetry run pytest \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

## Package Managers

### pip (Default)

```yaml
input:
  environment: python
  package_manager: pip
  cache: true
  cache_key: pip
```

### Poetry

```yaml
input:
  environment: python
  package_manager: poetry
  cache: true
  cache_key: poetry
```

### Pipenv

```yaml
input:
  environment: python
  package_manager: pipenv
  cache: true
  cache_key: pipenv
```

### PDM

```yaml
input:
  environment: python
  package_manager: pdm
  cache: true
  cache_key: pdm
```

## Linters

### ruff (Recommended)

```yaml
input:
  environment: python
  lint: true
  linter: ruff
```

### pylint

```yaml
input:
  environment: python
  lint: true
  linter: pylint
```

### flake8

```yaml
input:
  environment: python
  lint: true
  linter: flake8
```

### black

```yaml
input:
  environment: python
  lint: true
  linter: black
```

## Coverage Configuration

### Basic Coverage

```yaml
input:
  environment: python
  coverage_threshold: 80
  fail_under: 80
```

### Custom Coverage Settings

```yaml
input:
  environment: python
  coverage_threshold: 85
  fail_under: 85
  test_path: tests/unit
  src_path: app
  pytest_args: "-v --tb=short -m unit"
```

### Coverage Arguments Explained

| Argument | Description |
|----------|-------------|
| `--cov=src` | Measure coverage for the `src` directory |
| `--cov-report=term-missing` | Show missing lines in terminal |
| `--cov-report=xml` | Generate XML report for Codecov |
| `--cov-fail-under=80` | Fail if coverage is below 80% |

## Matrix Builds

### Multi-Version Testing

```yaml
input:
  environment: python
  version: "3.11"
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
    os: [ubuntu-latest]
```

### Generated Matrix Configuration

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
        os: [ubuntu-latest]
```

## Complete Examples

### Basic Pytest

```yaml
input:
  environment: python
  name: Python CI
  version: "3.11"
  coverage_threshold: 80
  fail_under: 80
```

### Poetry with Linting

```yaml
input:
  environment: python
  name: Python CI
  version: "3.12"
  package_manager: poetry
  coverage_threshold: 80
  fail_under: 80
  lint: true
  linter: ruff
  cache: true
```

### Matrix Testing

```yaml
input:
  environment: python
  name: Python CI
  version: "3.10"
  coverage_threshold: 80
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
    os: [ubuntu-latest]
```

### Custom Paths

```yaml
input:
  environment: python
  name: Tests
  version: "3.11"
  test_path: tests/unit
  src_path: app
  coverage_threshold: 85
  fail_under: 85
  pytest_args: "-v --tb=short -m unit"
```

### With Markers

```yaml
input:
  environment: python
  name: Python CI
  version: "3.11"
  pytest_markers:
    - unit
    - integration
  pytest_args: "-v --tb=short -m 'unit or integration'"
```

## Best Practices

1. **Set appropriate coverage thresholds**: 80% is a good starting point, increase as your test suite matures
2. **Use Poetry for dependency management**: Better lockfile and virtualenv handling
3. **Enable linting**: Catch issues early with ruff (fast) or pylint (thorough)
4. **Configure caching**: Significantly speeds up CI runs
5. **Use matrix builds**: Test across multiple Python versions
6. **Upload to Codecov**: Track coverage trends over time
7. **Set appropriate timeouts**: Prevent runaway jobs
8. **Use fail_ci_if_error**: Consider failing CI on Codecov errors

## Validation

The agent validates generated workflows:

- YAML syntax correctness
- Valid Python version strings
- Coverage threshold range (0-100)
- Valid pytest arguments
- Valid linter names
- Matrix configuration validity

## Related

- [GitHub Actions Generator](github-actions-generator.md) - General GitHub Actions generation
- [Integration Testing](integration-testing.md) - Test infrastructure
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
