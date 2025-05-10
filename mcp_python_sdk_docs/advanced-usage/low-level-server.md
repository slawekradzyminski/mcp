# Low-Level Server

For more control, you can use the lower-level server API:

```python
from mcp.protocol.schema import ResourceID, ToolID, PromptID
from mcp.server.base import MCPServer

# Create a server
server = MCPServer(name="Manual Server")


# Define resource handler
@server.resources.add(ResourceID("my-resource"))
async def handle_resource(path: str) -> str:
    return f"Resource: {path}"


# Define tool handler
@server.tools.add(ToolID("my-tool"))
async def handle_tool(params: dict) -> str:
    return f"Tool executed with {params}"


# Define prompt handler
@server.prompts.add(PromptID("my-prompt"))
async def handle_prompt(params: dict) -> str:
    return f"Prompt with {params}"
``` 