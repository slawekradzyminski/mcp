# Server Capabilities

Configure advanced server capabilities:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="Advanced Server",
    description="A server with advanced capabilities",
    capabilities={
        "stateless": True,
        "supports_concurrent_requests": True,
        "supports_progress_updates": True,
    },
    version="1.0.0",
    docs_url="https://example.com/docs",
    stateless_http=True,
)
``` 