"""Call command implementation for MCP CLI."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Dict

import click
import httpx

from .utils import is_server_running

DEFAULT_PORT = 7000


# Helper function to convert tool responses to JSON serializable objects
def _serialize_response(obj: Any) -> Any:
    """Convert MCP response objects to JSON serializable types.

    Args:
        obj: The object to serialize

    Returns:
        A JSON serializable representation of the object
    """
    # Handle MCP TextContent objects
    if hasattr(obj, "type") and hasattr(obj, "text"):
        return {"type": obj.type, "text": obj.text}
    # Handle lists (for collections of TextContent)
    elif isinstance(obj, list):
        return [_serialize_response(item) for item in obj]
    # Handle dictionaries (for nested structures)
    elif isinstance(obj, dict):
        return {k: _serialize_response(v) for k, v in obj.items()}
    # Return primitive types as-is
    return obj


@click.command(help="Invoke an MCP tool and print the result")
@click.option("--tool", "tool_name", required=True, help="Tool name to invoke")
@click.option(
    "--args",
    "args_json",
    default="{}",
    help='JSON string of arguments, e.g. \'{"url":"https://example.com"}\'',
)
@click.option("--port", default=DEFAULT_PORT, show_default=True, help="Server port")
@click.option("--json", "raw_json", is_flag=True, help="Output raw JSON")
def call(tool_name: str, args_json: str, port: int, raw_json: bool) -> None:
    """Synchronous wrapper around async `_call`.

    Args:
        tool_name: Name of the tool to invoke
        args_json: JSON string of arguments to pass to the tool
        port: Server port to connect to
        raw_json: Whether to output raw JSON instead of pretty-printed result
    """
    try:
        args_dict: Dict[str, Any] = json.loads(args_json)
    except json.JSONDecodeError as exc:
        click.echo(f"❌ Invalid JSON for --args: {exc}", err=True)
        sys.exit(1)

    try:
        result = asyncio.run(_call(tool_name, args_dict, port))
    except Exception as exc:  # noqa: BLE001
        click.echo(f"❌ {exc}", err=True)
        sys.exit(1)

    if raw_json:
        # Serialize the response to make it JSON compatible
        serialized_result = _serialize_response(result)
        click.echo(json.dumps(serialized_result, ensure_ascii=False, indent=2))
    else:
        _pretty_print(result)


async def _call(tool_name: str, args_dict: Dict[str, Any], port: int) -> Any:
    """Invoke `tool_name` either via HTTP (preferred) or in-process FastMCP.

    Args:
        tool_name: Name of the tool to invoke
        args_dict: Dictionary of arguments to pass to the tool
        port: Server port to connect to

    Returns:
        The result of the tool invocation

    Raises:
        RuntimeError: If the tool is not found or another error occurs
    """
    # Handle known tool name aliases
    tool_name_mapping = {
        "fetch": "http_fetch_tool",
        "search_docs": "search_docs_tool",
        "get_content": "get_local_content_tool",
    }

    # Map common names to actual tool names if necessary
    actual_tool_name = tool_name_mapping.get(tool_name, tool_name)

    if is_server_running(port):
        url = f"http://localhost:{port}/messages/"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url,
                json={
                    "msg_type": "call_tool",
                    "tool": actual_tool_name,
                    "args": args_dict,
                    "session_id": "cli-tool-call",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # Fallback – direct call against in-process server instance
    from mcp_simple_tool.server.handlers import mcp

    try:
        tools = {t.name: t for t in await mcp.list_tools()}

        # Try with mapped name first, then original name
        if actual_tool_name not in tools and tool_name in tools:
            actual_tool_name = tool_name

        if actual_tool_name not in tools:
            # Include both original and actual tool names in the error message
            tool_names_str = ", ".join(sorted(tools))
            if actual_tool_name != tool_name:
                raise RuntimeError(
                    f"Tool '{tool_name}' (tried as '{actual_tool_name}') "
                    f"not found. Available: {tool_names_str}"
                )
            else:
                raise RuntimeError(
                    f"Tool '{tool_name}' not found. Available: {tool_names_str}"
                )

        result = await mcp.call_tool(actual_tool_name, args_dict)
        return result
    except Exception as e:
        # If there's an error with the tool call itself, provide a more useful message
        if "is not JSON serializable" in str(e):
            # This is just a serialization issue, not a tool problem
            raise
        error_message = str(e)
        if "TypeError" in error_message:
            # Likely a parameter mismatch
            raise RuntimeError(
                f"Error calling tool '{actual_tool_name}': {error_message}. "
                f"Check parameter types and values."
            )
        else:
            raise RuntimeError(
                f"Error calling tool '{actual_tool_name}': {error_message}"
            )


def _pretty_print(obj: Any) -> None:
    """Human-friendly stdout representation.

    Args:
        obj: The object to pretty-print
    """
    import pprint

    click.echo(pprint.pformat(obj, compact=True, width=88))
