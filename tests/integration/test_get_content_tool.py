"""Integration tests for the get_local_content_tool."""

import pytest
from mcp_simple_tool.server.handlers import mcp


@pytest.mark.asyncio
async def test_get_content_registered():
    # given / when
    tools = {t.name for t in await mcp.list_tools()}

    # then
    assert "get_local_content_tool" in tools


@pytest.mark.asyncio
async def test_get_content_returns_full_text(tmp_path, monkeypatch):
    # given – arrange a fake doc
    fake = tmp_path / "x.md"
    fake.write_text("abc", encoding="utf-8")
    monkeypatch.setattr(
        "mcp_simple_tool.server.doc_reader.DOC_ROOT",
        tmp_path,
    )
    from mcp_simple_tool.server.handlers import get_local_content_tool

    # when
    out = await get_local_content_tool("x.md")

    # then
    assert "".join(t.text for t in out) == "abc"


@pytest.mark.asyncio
async def test_get_content_rejects_invalid_paths(tmp_path, monkeypatch):
    # given
    monkeypatch.setattr(
        "mcp_simple_tool.server.doc_reader.DOC_ROOT",
        tmp_path,
    )
    from mcp_simple_tool.server.handlers import get_local_content_tool

    # when / then
    with pytest.raises(ValueError, match="Parent traversal not allowed"):
        await get_local_content_tool("../something.md")


@pytest.mark.asyncio
async def test_get_content_rejects_invalid_extensions(tmp_path, monkeypatch):
    # given
    monkeypatch.setattr(
        "mcp_simple_tool.server.doc_reader.DOC_ROOT",
        tmp_path,
    )
    from mcp_simple_tool.server.handlers import get_local_content_tool

    # when / then
    with pytest.raises(ValueError, match="Unsupported extension"):
        await get_local_content_tool("file.exe")
