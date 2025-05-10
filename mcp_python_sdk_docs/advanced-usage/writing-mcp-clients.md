# Writing MCP Clients

You can create MCP clients to connect to any MCP server:

```python
import asyncio
from mcp.client import MCPClient
from mcp.protocol.schema import ToolID, ResourceID
from mcp.transports.basic.std_io import StdIOTransport

# Create client connected via stdio transport
client = MCPClient(transport=StdIOTransport())


async def main():
    # Connect to server
    await client.connect()

    # Get server capabilities
    caps = await client.get_capabilities()
    print(f"Connected to: {caps.name}")

    # Invoke a tool
    result = await client.invoke_tool(
        ToolID("calculator.add"),
        {"a": 1, "b": 2}
    )
    print(f"1 + 2 = {result}")

    # Read a resource
    data = await client.read_resource(ResourceID("config://settings"))
    print(f"Config: {data}")

    # Disconnect
    await client.disconnect()


asyncio.run(main())
``` 