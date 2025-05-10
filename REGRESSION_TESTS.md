# MCP Server Regression Tests

This document lists commands that can be run locally to perform a full regression test of the MCP server, matching the CI pipeline tests.

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

## Comprehensive Check

To run a full check similar to CI, execute these commands in sequence:

```bash
# Check formatting
python -m black --check mcp_simple_tool tests

# Run linters
python -m ruff check mcp_simple_tool tests
python -m mypy mcp_simple_tool

# Run all tests with coverage
python -m pytest --cov=mcp_simple_tool --cov-report=term
```

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