# Simple MCP Tool Server

A simple MCP server that exposes a website fetching tool using SSE transport.

## Installation

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package and dependencies
pip install -e .
```

## Usage

Start the server on the default port (7000) or specify a custom port:

```bash
# Using default port (7000)
python -m mcp_simple_tool

# Using custom port
python -m mcp_simple_tool --port 8000
```

The server exposes a tool named "fetch" that accepts one required argument:

- `url`: The URL of the website to fetch

## Server Management Scripts

The repository includes several helper scripts to manage the server:

- `restart_server.sh` - Stops any running server and starts a new one, waiting until it's responsive
- `check_server.sh` - Checks if the server is running and responsive
- `kill_server.sh` - Stops the server

Make them executable:

```bash
chmod +x *.sh
```

## Using with Cursor

This MCP server can be used with Cursor as a client. For setup:

1. Run the server in a terminal:
```bash
source venv/bin/activate
python -m mcp_simple_tool
# or use the restart script
./restart_server.sh
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
