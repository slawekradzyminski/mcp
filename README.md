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
pip install -r requirements.txt
```

## MCP Python SDK Documentation

The MCP Python SDK documentation has been split into smaller files and organized in the `docs/` directory. This structure makes it easier for AI agents to navigate and understand the SDK. The documentation covers:

- Core concepts (servers, resources, tools, etc.)
- Running MCP servers in different modes
- Examples and advanced usage
- And more!

## Usage

The package provides a command-line interface (CLI) with several commands to manage the MCP server:

### Starting the server

Start the server on the default port (7000) or specify a custom port:

```bash
# Using default port (7000)
python -m mcp_simple_tool start

# Using custom port
python -m mcp_simple_tool start --port 8000
```

### Managing the server

```bash
# Check if server is running
python -m mcp_simple_tool check [--port PORT]

# Stop the server
python -m mcp_simple_tool stop [--port PORT]

# Restart the server (stop and start)
python -m mcp_simple_tool restart [--port PORT]
```

The restart command will:
1. Stop any existing server on the specified port
2. Start a new server in the background
3. Wait until the server is responsive
4. Log output to server.log

### CLI quick reference

| Command | Purpose |
|---------|---------|
| `start` | Start the server |
| `stop`  | Stop the server |
| `check` | Health-check |
| `restart` | Stop & start |
| `call` | Invoke a tool locally or against a running server |

## Server Tools

The server exposes the following tools:

- **fetch**: Fetches a website and returns its content
  - `url`: The URL of the website to fetch (required)

- **search_docs**: Semantic search across SDK documentation files
  - `query`: Search phrase or question (required)
  - `k`: Number of top matches to return (optional, default = 3)

### Testing a tool

You can test the tools using the CLI:

```bash
# Test the fetch tool
python -m mcp_simple_tool call --tool fetch --args '{"url":"https://awesome-testing.com"}'

# Test the search_docs tool
python -m mcp_simple_tool call --tool search_docs --args '{"query":"Context object"}'
```

## Development Setup

For development, install additional tools:

```bash
pip install -e .
pip install -r requirements.txt
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

### Semantic Search Index

For the search_docs tool, you can manually build or rebuild the vector index:

```bash
# Build or rebuild the semantic search index
python scripts/build_doc_index.py
```

The index is built automatically on first tool use if it doesn't exist.

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
        handlers.py      # Tool implementations
        http.py          # HTTP utilities
    semantic_search/     # Semantic search functionality
        __init__.py      # Package initialization
        indexing.py      # Build and persist vector store
        search.py        # Load index and query helpers
```

## Using with Cursor

This MCP server can be used with Cursor as a client. For setup:

1. Run the server in a terminal:
```bash
source venv/bin/activate
python -m mcp_simple_tool start
# or use the restart command
python -m mcp_simple_tool restart
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
