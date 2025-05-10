"""Utility functions shared by CLI commands."""

from __future__ import annotations

import os
import signal
import time
from typing import Optional

import requests
from requests.exceptions import RequestException


def is_server_running(port: int) -> bool:
    """Return *True* if an HTTP(SSE) server listens on `port`."""
    try:
        resp = requests.head(f"http://localhost:{port}/sse", timeout=(1, 2))
        return 200 <= resp.status_code < 500
    except RequestException:
        return False


def get_server_pid(port: int) -> Optional[int]:
    """Return PID of a process **LISTEN**ing on `port`, else *None*."""
    import subprocess

    try:
        out = subprocess.check_output(["lsof", "-i", f":{port}", "-sTCP:LISTEN"])
        lines = out.decode().strip().splitlines()
        if len(lines) > 1:
            return int(lines[1].split()[1])
    except (subprocess.SubprocessError, ValueError, IndexError):
        pass
    return None


def is_process_running(pid: int) -> bool:
    """Return *True* if process with `pid` exists."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def graceful_kill(pid: int, *, timeout: float = 5.0) -> bool:
    """SIGTERM then SIGKILL after `timeout` sec; *True* if dead."""
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not is_process_running(pid):
            return True
        time.sleep(0.2)
    os.kill(pid, signal.SIGKILL)
    return not is_process_running(pid)


# Re-export utilities for backward compatibility
__all__ = ["is_server_running", "get_server_pid", "is_process_running", "graceful_kill"]
