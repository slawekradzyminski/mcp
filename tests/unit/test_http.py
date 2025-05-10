"""Tests for HTTP utilities."""

import httpx
import pytest
import respx

from mcp_simple_tool.server.http import fetch


@respx.mock
@pytest.mark.asyncio
async def test_fetch_success():
    """Test successful website fetch."""
    # given
    route = respx.get("https://example.com").mock(
        return_value=httpx.Response(200, text="ok")
    )

    # when
    text = await fetch("https://example.com", headers={"User-Agent": "Test Agent"})

    # then
    assert text == "ok"
    assert route.called
    assert route.calls[0].request.headers["User-Agent"] == "Test Agent"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_error():
    """Test error handling in fetch."""
    # given
    route = respx.get("https://example.com").mock(return_value=httpx.Response(404))

    # when/then
    with pytest.raises(httpx.HTTPStatusError):
        await fetch("https://example.com", headers={})
