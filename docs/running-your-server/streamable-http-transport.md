# Streamable HTTP Transport

> **Note**: Streamable HTTP transport is superseding SSE transport for production deployments.

```python
from mcp.server.fastmcp import FastMCP

# Stateful server (maintains session state)
mcp = FastMCP("StatefulServer")

# Stateless server (no session persistence)
mcp = FastMCP("StatelessServer", stateless_http=True)

# Run server with streamable_http transport
mcp.run(transport="streamable-http")
```

You can mount multiple FastMCP servers in a FastAPI application:

```python
# echo.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="EchoServer", stateless_http=True)


@mcp.tool(description="A simple echo tool")
def echo(message: str) -> str:
    return f"Echo: {message}"
```

```python
# math.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MathServer", stateless_http=True)


@mcp.tool(description="A simple add tool")
def add_two(n: int) -> str:
    return n + 2
```

```python
# main.py
from fastapi import FastAPI
from mcp.echo import echo
from mcp.math import math


app = FastAPI()

# Use the session manager's lifespan
app = FastAPI(lifespan=lambda app: echo.mcp.session_manager.run())
app.mount("/echo", echo.mcp.streamable_http_app())
app.mount("/math", math.mcp.streamable_http_app())
```

The streamable HTTP transport supports:
- Stateful and stateless operation modes
- Resumability with event stores
- JSON or SSE response formats  
- Better scalability for multi-node deployments 