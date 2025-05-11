"""Tests for doc_reader module."""

import pytest
from mcp_simple_tool.server.doc_reader import read_local_doc, DOC_ROOT


def test_read_local_doc_ok(tmp_path, monkeypatch):
    # given – create temp doc tree
    (tmp_path / "foo.md").write_text("hello", encoding="utf-8")
    monkeypatch.setattr("mcp_simple_tool.server.doc_reader.DOC_ROOT", tmp_path)

    # when
    chunks = read_local_doc("foo.md")

    # then
    assert len(chunks) == 1
    assert chunks[0].text == "hello"


@pytest.mark.parametrize("bad", ["../../evil.txt", "nosuch.md", "file.exe"])
def test_read_local_doc_errors(tmp_path, monkeypatch, bad):
    # given - setup test environment
    monkeypatch.setattr("mcp_simple_tool.server.doc_reader.DOC_ROOT", tmp_path)

    # when / then - expect an exception
    with pytest.raises(Exception):
        read_local_doc(bad)


def test_chunking_large_text(tmp_path, monkeypatch):
    # given - create large text file
    large_text = "a" * 2500  # Exceeds the chunk size of 1000
    (tmp_path / "large.md").write_text(large_text, encoding="utf-8")
    monkeypatch.setattr("mcp_simple_tool.server.doc_reader.DOC_ROOT", tmp_path)

    # when
    chunks = read_local_doc("large.md")

    # then
    assert len(chunks) == 3
    assert chunks[0].text == "a" * 1000
    assert chunks[1].text == "a" * 1000
    assert chunks[2].text == "a" * 500
