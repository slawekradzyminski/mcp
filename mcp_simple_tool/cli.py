"""Command-line interface for MCP Server."""

import os
import signal
import socket
import sys
import time
from typing import Optional

import click
import requests
import uvicorn
from requests.exceptions import RequestException

from .server.app import starlette_app
from .server.config import Settings


def is_server_running(port: int) -> bool:
    """
    Check if the server is running on the specified port.

    Args:
        port: The port to check

    Returns:
        True if a server is responding on the port, False otherwise
    """
    try:
        # Use HEAD request with timeout to avoid hanging on SSE connection
        response = requests.head(
            f"http://localhost:{port}/sse",
            timeout=(1, 2),
        )
        # Accept 200 or any 4xx status as sign that server is running
        return 200 <= response.status_code < 500
    except RequestException:
        return False


@click.group()
def cli() -> None:
    """MCP Simple Tool command line interface."""
    pass


@cli.command(help="Start the MCP server")
@click.option("--port", default=Settings().port, help="Port to listen on for SSE")
@click.option("--daemon", is_flag=True, help="Run server as a background daemon")
def start(port: int, daemon: bool = False) -> None:
    """
    Start the MCP server.

    Args:
        port: The port to run the server on
        daemon: Whether to run as a background daemon
    """
    # Check if server is already running
    if is_server_running(port):
        print(f"Server is already running on port {port}")
        return

    # Also check if any process is bound to this port
    if get_server_pid(port):
        print(f"Port {port} is already in use, but the server is not responding")
        print("Use 'stop' command to terminate the existing process first")
        sys.exit(1)

    # For daemon mode, start in background
    if daemon:
        import subprocess

        # Create detached process without the daemon flag
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
        print("Server started in background mode. Monitor with: tail -f server.log")
        print(f"Server URL: http://localhost:{port}/sse")
        return

    # For foreground mode, run directly
    print(f"Starting MCP website fetcher server on port {port}")
    print(f"Server URL: http://localhost:{port}/sse")

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)


@cli.command(help="Check if the MCP server is running")
@click.option("--port", default=Settings().port, help="Port to check")
def check(port: int) -> None:
    """
    Check if the MCP server is running.

    Args:
        port: The port to check
    """
    # First check if the server is responding to HTTP requests
    if is_server_running(port):
        pid = get_server_pid(port)
        if pid:
            print(f"Server process found with PID: {pid}")
        else:
            print("Server is responding but PID could not be determined")

        print(f"Server is up and running at http://localhost:{port}/sse")
        return

    # If not responding to HTTP, check if a process is bound to the port
    pid = get_server_pid(port)
    if pid:
        print(f"Server process found with PID: {pid}")
        print("Server process is running but not responding properly")
        sys.exit(1)
    else:
        print(f"No server process found running on port {port}")
        sys.exit(1)


@cli.command(help="Stop the running MCP server")
@click.option("--port", default=Settings().port, help="Port the server is running on")
@click.option(
    "--force", is_flag=True, help="Force kill the process without graceful shutdown"
)
def stop(port: int, force: bool = False) -> None:
    """
    Stop the MCP server.

    Args:
        port: The port the server is running on
        force: Whether to force kill the process
    """
    print(f"Stopping MCP server on port {port}...")
    pid = get_server_pid(port)
    if pid:
        print(f"Found server process: {pid} - terminating...")
        try:
            # If force, skip the graceful shutdown
            if force:
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                if is_process_running(pid):
                    print("ERROR: Failed to kill server process")
                    sys.exit(1)
                else:
                    print("Server terminated successfully with force kill")
                return

            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)

            # Give it time to terminate gracefully
            for i in range(10):  # 10 x 0.5 seconds = 5 seconds timeout
                time.sleep(0.5)
                if not is_process_running(pid):
                    print("Server terminated successfully")
                    return

            # If still running, force kill
            print("Server process didn't terminate gracefully, force killing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)

            if is_process_running(pid):
                print("ERROR: Failed to kill server process")
                sys.exit(1)
            else:
                print("Server terminated successfully with force kill")
        except OSError as e:
            print(f"Error terminating process: {e}")
            sys.exit(1)
    else:
        # No process found but check if there's still an HTTP server responding
        if is_server_running(port):
            print(
                f"Server is responding on port {port} but no process found to terminate"
            )
            print("You may need to manually identify and terminate the process")
            sys.exit(1)
        else:
            print(f"No server found running on port {port}")


@cli.command(help="Restart the MCP server")
@click.option("--port", default=Settings().port, help="Port to run the server on")
def restart(port: int) -> None:
    """
    Restart the MCP server.

    Args:
        port: The port to run the server on
    """
    # First stop any running server
    if get_server_pid(port) or is_server_running(port):
        print(f"Stopping existing server on port {port}...")
        
        # Handle stopping directly instead of calling stop command
        pid = get_server_pid(port)
        if pid:
            print(f"Found server process: {pid} - terminating...")
            try:
                # Use force kill directly to ensure the process is fully terminated
                print("Using force kill to ensure clean termination...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)  # Give it time to fully terminate

                if is_process_running(pid):
                    print("ERROR: Failed to kill server process")
                    sys.exit(1)
                else:
                    print("Server terminated successfully")
            except OSError as e:
                print(f"Error terminating process: {e}")
                sys.exit(1)
        else:
            # No process found but check if there's still an HTTP server responding
            if is_server_running(port):
                print(f"Server is responding on port {port} but no process found to terminate")
                print("You may need to manually identify and terminate the process")
                sys.exit(1)
            else:
                print(f"No server found running on port {port}")
    else:
        print(f"No server found running on port {port}")

    # Make sure port is available before starting
    print("Waiting for port to be available...")
    max_retries = 10  # Increase max retries
    for retry in range(max_retries):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Add socket option to reuse address
            s.bind(("0.0.0.0", port))
            s.close()
            print(f"Port {port} is now available")
            break
        except socket.error:
            if retry < max_retries - 1:
                print(f"Port {port} still in use, waiting... (attempt {retry + 1}/{max_retries})")
                time.sleep(3)  # Increase delay between attempts to 3 seconds
            else:
                print(f"Error: Port {port} is still in use after {max_retries} attempts. Unable to start server.")
                sys.exit(1)
        finally:
            try:
                s.close()
            except:
                pass  # Ignore errors in socket closing

    # Start server in daemon mode
    print(f"Starting MCP server on port {port}...")

    # Use subprocess directly instead of using start.callback with daemon
    import subprocess

    # Create log file
    log_file = open("server.log", "w")

    # Use python -m to ensure proper module import
    cmd = [sys.executable, "-m", "mcp_simple_tool", "start", "--port", str(port)]

    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        stdin=subprocess.DEVNULL,
    )

    # Wait briefly to allow the process to start
    time.sleep(1)

    # Check if process is still running
    if proc.poll() is not None:
        print(f"Error: Server process exited with code {proc.returncode}")
        print("Check server.log for details")
        sys.exit(1)

    # Wait for server to become responsive
    max_retries = 10
    retry_interval = 2
    print("Waiting for server to become responsive...")

    for i in range(1, max_retries + 1):
        print(f"Attempt {i} of {max_retries}...")
        if is_server_running(port):
            print("Server is up and running!")
            print(f"Server URL: http://localhost:{port}/sse")
            return

        # Check if process is still alive
        if proc.poll() is not None:
            print(f"Error: Server process exited with code {proc.returncode}")
            print("Check server.log for details")
            sys.exit(1)

        if i == max_retries:
            print(
                "Server process is running but not responding. "
                "Check server.log for errors."
            )
            sys.exit(1)

        time.sleep(retry_interval)


def get_server_pid(port: int) -> Optional[int]:
    """
    Get the PID of a process listening on the specified port.

    Args:
        port: The port to check

    Returns:
        The PID of the process or None if not found
    """
    try:
        import subprocess

        # Look for processes that have the port open for listening (LISTEN state)
        output = subprocess.check_output(["lsof", "-i", f":{port}", "-sTCP:LISTEN"])

        # Parse the output to find process IDs
        lines = output.decode("utf-8").strip().split("\n")
        if len(lines) > 1:  # Skip header line
            # Split the second line by whitespace and get the PID
            pid_str = lines[1].split()[1]
            return int(pid_str)
    except (subprocess.SubprocessError, ValueError, IndexError):
        pass
    return None


def is_process_running(pid: int) -> bool:
    """
    Check if a process with the specified PID is running.

    Args:
        pid: The process ID to check

    Returns:
        True if the process is running, False otherwise
    """
    try:
        # Sending signal 0 is a way to check if the process exists
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main() -> int:
    """Main entry point for the CLI."""
    cli()
    return 0
