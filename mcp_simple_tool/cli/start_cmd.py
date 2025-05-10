"""Start command implementation for MCP CLI."""

from __future__ import annotations

import subprocess
import sys

import click
import uvicorn

from ..server.config import Settings
from .utils import get_server_pid, is_server_running


@click.command(help="Start the MCP server")
@click.option("--port", default=Settings().port, show_default=True, help="Port for SSE")
@click.option("--daemon", is_flag=True, help="Run in background")
def start(port: int, daemon: bool) -> None:
    """Start the MCP server.

    Args:
        port: The port to run the server on
        daemon: Whether to run as a background daemon
    """
    # Check if server is already running
    if is_server_running(port):
        click.echo(f"Server is already running on port {port}")
        return

    # Also check if any process is bound to this port
    if get_server_pid(port):
        click.echo(f"Port {port} is already in use, but the server is not responding")
        click.echo("Use 'stop' command to terminate the existing process first")
        sys.exit(1)

    # For daemon mode, start in background
    if daemon:
        log_file = open("server.log", "w")

        # Use python -m to ensure proper module import
        cmd = [sys.executable, "-m", "mcp_simple_tool", "start", "--port", str(port)]

        subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
            stdin=subprocess.DEVNULL,
        )
        click.echo(
            "Server started in background mode. Monitor with: tail -f server.log"
        )
        click.echo(f"Server URL: http://localhost:{port}/sse")
        return

    # For foreground mode, run directly
    click.echo(f"Starting MCP website fetcher server on port {port}")
    click.echo(f"Server URL: http://localhost:{port}/sse")

    # Run the server
    from ..server.app import starlette_app

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
