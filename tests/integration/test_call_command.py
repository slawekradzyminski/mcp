"""Integration tests for the call command."""

from __future__ import annotations

import subprocess
import sys
from typing import Dict, List, Any

import pytest

from tests.helpers import TestClient


@pytest.fixture
def test_client():
    """Fixture that creates a test client."""
    with TestClient() as client:
        yield client


def test_call_direct_search_docs():
    """Test calling the search_docs tool directly via the CLI."""
    # given
    # Simple query that should return results from the docs
    query = "server"

    # when
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_simple_tool",
            "call",
            "--tool",
            "search_docs",
            "--args",
            f'{{"query":"{query}"}}',
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    # then
    assert result.returncode == 0
    assert "text" in result.stdout  # Results should contain text field
    assert "metadata" in result.stdout  # Results should contain metadata


def test_call_with_server(test_client):
    """Test calling a tool against the running test server."""
    # given
    # The test client starts a server on a random port
    port = test_client.port

    # when
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_simple_tool",
            "call",
            "--tool",
            "fetch",
            "--args",
            '{"url":"https://httpbin.org/get"}',
            "--port",
            str(port),
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    # then
    assert result.returncode == 0
    assert "url" in result.stdout  # Response should contain the URL
    assert "httpbin.org" in result.stdout  # Confirm it's from the right service


def test_call_invalid_tool(test_client):
    """Test calling a non-existent tool."""
    # given
    port = test_client.port

    # when
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mcp_simple_tool",
            "call",
            "--tool",
            "non_existent_tool",
            "--args",
            "{}",
            "--port",
            str(port),
        ],
        capture_output=True,
        text=True,
    )

    # then
    assert result.returncode != 0  # Should exit with non-zero code
    assert "❌" in result.stderr  # Should show error
