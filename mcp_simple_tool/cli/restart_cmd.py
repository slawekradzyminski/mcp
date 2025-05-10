"""Restart command implementation for MCP CLI."""

from __future__ import annotations

import os
import signal
import socket
import sys
import time

import click

from ..server.config import Settings
from .utils import get_server_pid, is_process_running, is_server_running


@click.command(help="Restart the MCP server")
@click.option("--port", default=Settings().port, help="Port to run the server on")
def restart(port: int) -> None:
    """Restart the MCP server.

    Args:
        port: The port to run the server on
    """
    # First stop any running server
    if get_server_pid(port) or is_server_running(port):
        click.echo(f"Stopping existing server on port {port}...")

        # Handle stopping directly
        pid = get_server_pid(port)
        if pid:
            click.echo(f"Found server process: {pid} - terminating...")
            try:
                # Use force kill to ensure the process is fully terminated
                click.echo("Using force kill to ensure clean termination...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)  # Give it time to fully terminate

                if is_process_running(pid):
                    click.echo("ERROR: Failed to kill server process")
                    sys.exit(1)
                else:
                    click.echo("Server terminated successfully")
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
                click.echo(
                    "You may need to manually identify and terminate the process"
                )
                sys.exit(1)
            else:
                click.echo(f"No server found running on port {port}")
    else:
        click.echo(f"No server found running on port {port}")

    # Make sure port is available before starting
    click.echo("Waiting for port to be available...")
    max_retries = 10
    for retry in range(max_retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            s.close()
            click.echo(f"Port {port} is now available")
            break
        except OSError:
            if retry < max_retries - 1:
                click.echo(f"Port {port} still in use, waiting...")
                time.sleep(0.5)
            else:
                click.echo(f"Port {port} could not be freed, giving up")
                sys.exit(1)

    # Start the server in daemon mode to prevent blocking the CLI
    import subprocess

    log_file = open("server.log", "w")

    # Use python -m to ensure proper module import
    cmd = [
        sys.executable,
        "-m",
        "mcp_simple_tool",
        "start",
        "--port",
        str(port),
        "--daemon",
    ]

    subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        stdin=subprocess.DEVNULL,
    )
    click.echo("Server started in background mode. Monitor with: tail -f server.log")
    click.echo(f"Server URL: http://localhost:{port}/sse")

    # Wait for the server to become responsive
    click.echo("Waiting for server to respond...")
    for i in range(10):
        if is_server_running(port):
            click.echo(f"Server is now running on port {port}")
            return
        time.sleep(0.5)

    click.echo("Warning: Server was started but is not responding to HTTP requests")
    click.echo("Check server.log for details")
