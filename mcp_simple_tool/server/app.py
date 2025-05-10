"""Starlette application with SSE transport for MCP."""

from __future__ import annotations

from .handlers import mcp

# The FastMCP's sse_app() method provides the complete ASGI app for SSE.
# It internally handles the SseServerTransport, routes, and server run logic.
starlette_app = mcp.sse_app()
