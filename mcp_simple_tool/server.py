import click
import uvicorn
from mcp.server.fastmcp import FastMCP


@click.command()
@click.option("--port", default=7000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="sse",
    help="Transport type (only SSE is supported)",
)
def main(port: int, transport: str) -> int:
    mcp = FastMCP("mcp-website-fetcher-sse")

    if transport != "sse":
        print("Warning: Only SSE transport is supported. Using SSE transport.")

    print(f"Starting MCP website fetcher server on port {port}")
    print(f"Server URL: http://localhost:{port}/sse")

    starlette_app = mcp.sse_app()
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0
