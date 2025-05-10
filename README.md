# Simple MCP Tool Server

A simple MCP server that exposes a website fetching tool using SSE transport.

## Requirements

- Python 3.10 or higher (tested on Python 3.13)

## Installation

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package and dependencies
pip install -e .
```

## MCP Python SDK Documentation

The MCP Python SDK documentation has been split into smaller files and organized in the `mcp_python_sdk_docs/` directory. This structure makes it easier for AI agents to navigate and understand the SDK. The documentation covers:

- Core concepts (servers, resources, tools, etc.)
- Running MCP servers in different modes
- Examples and advanced usage
- And more!

Check out the [index file](mcp_python_sdk_docs/index.md) for the complete table of contents.

## Usage

The package provides a command-line interface (CLI) with several commands to manage the MCP server:

### Starting the server

Start the server on the default port (7000) or specify a custom port:

```bash
# Using default port (7000)
mcp-simple-tool start

# Using custom port
mcp-simple-tool start --port 8000
```

### Managing the server

```bash
# Check if server is running
mcp-simple-tool check [--port PORT]

# Stop the server
mcp-simple-tool stop [--port PORT]

# Restart the server (stop and start)
mcp-simple-tool restart [--port PORT]
```

The restart command will:
1. Stop any existing server on the specified port
2. Start a new server in the background
3. Wait until the server is responsive
4. Log output to server.log

## Server Tool

The server exposes a tool named "fetch" that accepts one required argument:

- `url`: The URL of the website to fetch

## Development Setup

For development, install additional tools:

```bash
pip install -e .
pip install black ruff mypy pytest pytest-asyncio pytest-timeout respx pydantic pydantic-settings
```

Use the Makefile for common tasks:

```bash
# Format code
make fmt

# Run linters
make lint

# Run tests
make test
```

The test suite has a built-in 20-second timeout for all tests to prevent hanging, especially with SSE endpoints. For individual tests, a more strict timeout can be specified using the `@pytest.mark.timeout(seconds)` decorator.

## Project Architecture

```
mcp_simple_tool/
    __init__.py          # Package initialization
    __main__.py          # Entry point when run as module
    cli.py               # Command-line interface
    server/              # Server implementation
        __init__.py      # Server package initialization
        app.py           # ASGI application setup
        config.py        # Configuration settings
        handlers.py      # Tool implementation
        http.py          # HTTP utilities
```

## Using with Cursor

This MCP server can be used with Cursor as a client. For setup:

1. Run the server in a terminal:
```bash
source venv/bin/activate
mcp-simple-tool start
# or use the restart command
mcp-simple-tool restart
```

2. Configure Cursor by creating a `.cursor/mcp.json` file:
```json
{
  "mcpServers": {
    "website-fetcher-sse": {
      "url": "http://localhost:7000/sse"
    }
  }
}
```

3. Mention the server in your prompts when using Cursor
