# MCP Primitives

For advanced use cases, you can work directly with MCP protocol primitives:

```python
import json
from typing import Dict, Any
from mcp.protocol.schema import (
    MessageType, 
    ClientMessage, 
    ServerMessage,
    InvokeToolRequest,
    InvokeToolResponse,
    ReadResourceRequest,
    ReadResourceResponse,
    ToolID,
    ResourceID,
)

# Build a tool invocation message
tool_msg: ClientMessage = {
    "msg_type": MessageType.INVOKE_TOOL_REQUEST,
    "msg_id": "msg_1",
    "invoke_tool_request": InvokeToolRequest(
        tool_id=ToolID("add"),
        params={"a": 1, "b": 2},
    ),
}

# Serialize for transport
message_json = json.dumps(tool_msg)
print(message_json)

# Parse server response
response_json = '{"msg_type": "invoke_tool_response", "msg_id": "resp_1", "in_reply_to": "msg_1", "invoke_tool_response": {"result": 3}}'
response_dict: Dict[str, Any] = json.loads(response_json)
response: ServerMessage = response_dict
result = response["invoke_tool_response"]["result"]
print(f"Result: {result}")
``` 