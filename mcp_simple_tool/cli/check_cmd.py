"""Check command implementation for MCP CLI."""

from __future__ import annotations

import sys

import click

from ..server.config import Settings
from .utils import get_server_pid, is_server_running


@click.command(help="Check if the MCP server is running")
@click.option("--port", default=Settings().port, help="Port to check")
def check(port: int) -> None:
    """Check if the MCP server is running.

    Args:
        port: The port to check
    """
    # First check if the server is responding to HTTP requests
    if is_server_running(port):
        pid = get_server_pid(port)
        if pid:
            click.echo(f"Server process found with PID: {pid}")
        else:
            click.echo("Server is responding but PID could not be determined")

        click.echo(f"Server is up and running at http://localhost:{port}/sse")
        return

    # If not responding to HTTP, check if a process is bound to the port
    pid = get_server_pid(port)
    if pid:
        click.echo(f"Server process found with PID: {pid}")
        click.echo("Server process is running but not responding properly")
        sys.exit(1)
    else:
        click.echo(f"No server process found running on port {port}")
        sys.exit(1)
