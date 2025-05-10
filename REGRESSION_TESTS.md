# MCP Server Regression Tests

This document lists commands that can be run locally to perform a full regression test of the MCP server, matching the CI pipeline tests.

## Makefile Shortcuts

The project includes a Makefile with shortcuts for common tasks:

```bash
# Format code with Black
make fmt

# Check formatting without modifying files
make fmt-check

# Run linting (ruff and mypy)
make lint

# Run tests
make test

# Run all checks (equivalent to CI)
make ci
# or
make check
```

## Code Quality Checks

### Formatting

```bash
# Check code formatting with Black
python -m black --check mcp_simple_tool tests

# Apply formatting fixes if needed
python -m black mcp_simple_tool tests
```

### Linting

```bash
# Run Ruff linter
python -m ruff check mcp_simple_tool tests

# Run mypy type checker
python -m mypy mcp_simple_tool
```

#### MyPy Type Checking

MyPy requires type stubs for some third-party libraries. Make sure to install them:

```bash
# Install required type stubs
pip install types-requests

# Alternatively, let mypy install missing type stubs automatically
mypy --install-types mcp_simple_tool
```

Type checking issues can be suppressed using `# type: ignore` comments for third-party code or cases where types cannot be properly annotated.

## Tests

### Unit Tests

```bash
# Run unit tests
python -m pytest tests/unit

# Run unit tests with coverage report
python -m pytest tests/unit --cov=mcp_simple_tool --cov-report=term
```

### Integration Tests

```bash
# Run integration tests
python -m pytest tests/integration

# Run specific integration test
python -m pytest tests/integration/test_server.py -v
```

### Combined Tests

```bash
# Run all tests
python -m pytest

# Run all tests with coverage report
python -m pytest --cov=mcp_simple_tool --cov-report=term
```

## Comprehensive Check (CI Equivalent)

To run a full check similar to CI, execute these commands in sequence:

```bash
# Install dependencies
python -m pip install --upgrade pip
pip install -e .
pip install -r requirements.txt

# Run all checks using Makefile
make ci

# Alternatively, run the commands manually:
python -m black --check mcp_simple_tool tests
python -m ruff check mcp_simple_tool
python -m mypy mcp_simple_tool
python -m pytest -q
```

The CI workflow runs these checks on Python 3.13 in Ubuntu, but they should work consistently on all supported platforms.

## Running the Server

```bash
# Start server in foreground mode
python -m mcp_simple_tool start

# Start server in background mode
python -m mcp_simple_tool start --daemon

# Check if server is running
python -m mcp_simple_tool check

# Stop the server
python -m mcp_simple_tool stop

# Restart the server
python -m mcp_simple_tool restart
``` 