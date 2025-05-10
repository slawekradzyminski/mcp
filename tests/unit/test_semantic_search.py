"""Unit tests for the semantic search functionality."""

import pathlib
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from mcp_simple_tool.semantic_search import indexing, search


@patch("mcp_simple_tool.semantic_search.indexing.TfidfVectorizer")
def test_chunker_roundtrip(mock_vectorizer: MagicMock) -> None:
    """Test that the chunking function splits text correctly."""
    # given
    txt = "abcdef" * 100

    # when
    pieces = indexing.chunk_text(txt)

    # then
    assert len(pieces) > 1
    assert "".join(pieces[:1]) in txt


def test_iter_files_finds_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that iter_files finds documentation files."""
    # given
    mock_doc_dir = MagicMock(spec=pathlib.Path)
    test_files = [
        MagicMock(spec=pathlib.Path, suffix=".md", is_file=lambda: True),
        MagicMock(spec=pathlib.Path, suffix=".txt", is_file=lambda: True),
        MagicMock(spec=pathlib.Path, suffix=".yml", is_file=lambda: True),
        MagicMock(spec=pathlib.Path, suffix=".yaml", is_file=lambda: True),
        MagicMock(
            spec=pathlib.Path, suffix=".py", is_file=lambda: True
        ),  # should be ignored
        MagicMock(spec=pathlib.Path, suffix=".md", is_file=lambda: False),  # directory
    ]
    mock_doc_dir.rglob.return_value = test_files
    monkeypatch.setattr(indexing, "DOC_DIR", mock_doc_dir)

    # when
    result = list(indexing.iter_files())

    # then
    assert len(result) == 4  # Only .md, .txt, .yml, .yaml files
    mock_doc_dir.rglob.assert_called_once_with("*")


def test_cosine_similarity() -> None:
    """Test the cosine similarity search function."""
    # given
    # Create a small test matrix and a query vector
    matrix = np.array(
        [
            [1.0, 0.0, 0.0],  # Document 1
            [0.5, 0.5, 0.0],  # Document 2
            [0.3, 0.3, 0.3],  # Document 3
        ],
        dtype=np.float32,
    )

    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)  # Vector matching Document 1

    # when
    res = search._cosine_similarity_search(matrix, query, k=2)

    # then
    assert len(res) == 2
    # Check that Document 1 is the top result
    assert res[0][0] == 0
    assert res[0][1] > 0.9  # Should be close to 1.0 (exact match)
    # Document 2 should be the second best match
    assert res[1][0] == 1


@patch("mcp_simple_tool.semantic_search.search._load_assets")
def test_semantic_search(mock_load_assets: MagicMock) -> None:
    """Test the semantic search function with mocked assets."""
    # given
    mock_vectorizer = MagicMock()
    mock_vec_sparse = MagicMock()
    mock_vec_sparse.toarray.return_value = np.array([[1, 0, 0]], dtype="float32")
    mock_vectorizer.transform.return_value = mock_vec_sparse

    mock_matrix = MagicMock()
    mock_meta = [
        {"file": "file1.md", "text": "content1"},
        {"file": "file2.md", "text": "content2"},
        {"file": "file3.md", "text": "content3"},
    ]
    mock_load_assets.return_value = (
        mock_vectorizer,
        mock_matrix,
        mock_meta,
    )

    # Mock _cosine_similarity_search to return predetermined results
    with patch("mcp_simple_tool.semantic_search.search._cosine_similarity_search") as mock_cosine:
        mock_cosine.return_value = [(0, 0.9), (2, 0.7)]
        
        # when
        results = search.semantic_search("test query", k=2)

    # then
    assert len(results) == 2
    assert results[0]["file"] == "file1.md"
    assert results[0]["score"] == 0.9
    assert results[0]["excerpt"] == "content1"
    assert results[1]["file"] == "file3.md"
