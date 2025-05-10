"""Starlette application with SSE transport for MCP."""

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

from .config import Settings
from .handlers import server

settings = Settings()
sse = SseServerTransport("/messages/")


async def handle_sse(request):
    """Handle SSE connections."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())
    return Response()


starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)
