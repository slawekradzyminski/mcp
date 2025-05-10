"""Stop command implementation for MCP CLI."""

from __future__ import annotations

import os
import signal
import sys
import time

import click

from ..server.config import Settings
from .utils import get_server_pid, graceful_kill, is_process_running, is_server_running


@click.command(help="Stop the running MCP server")
@click.option("--port", default=Settings().port, help="Port the server is running on")
@click.option(
    "--force", is_flag=True, help="Force kill the process without graceful shutdown"
)
def stop(port: int, force: bool = False) -> None:
    """Stop the MCP server.

    Args:
        port: The port the server is running on
        force: Whether to force kill the process
    """
    click.echo(f"Stopping MCP server on port {port}...")
    pid = get_server_pid(port)

    if pid:
        click.echo(f"Found server process: {pid} - terminating...")
        try:
            # If force, skip the graceful shutdown
            if force:
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                if is_process_running(pid):
                    click.echo("ERROR: Failed to kill server process")
                    sys.exit(1)
                else:
                    click.echo("Server terminated successfully with force kill")
                return

            # Try graceful shutdown
            killed = graceful_kill(pid)
            if killed:
                click.echo("Server terminated successfully")
                return
            else:
                click.echo("ERROR: Failed to kill server process")
                sys.exit(1)

        except OSError as e:
            click.echo(f"Error terminating process: {e}")
            sys.exit(1)
    else:
        # No process found but check if there's still an HTTP server responding
        if is_server_running(port):
            click.echo(
                f"Server is responding on port {port} "
                "but no process found to terminate"
            )
            click.echo("You may need to manually identify and terminate the process")
            sys.exit(1)
        else:
            click.echo(f"No server found running on port {port}")
