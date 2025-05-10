"""Build and persist the vector store for semantic search."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Export constants and functions
__all__ = [
    "build_index",
    "chunk_text",
    "iter_files",
    "Chunk",
    "DOC_DIR",
    "INDEX_PATH",
    "META_PATH",
    "MODEL_NAME",
]

DOC_DIR = pathlib.Path(__file__).resolve().parents[2] / "mcp_python_sdk_docs"
INDEX_PATH = DOC_DIR / ".vector_index.npy"
META_PATH = DOC_DIR / ".vector_meta.jsonl"
CHUNK_SIZE = 400  # characters, tweak as needed
OVERLAP = 40  # characters to preserve context

MODEL_NAME = "tfidf-vectorizer"  # Using TF-IDF instead of transformer models


@dataclass
class Chunk:
    """Represents a chunk of text from a file."""

    file_path: str
    start: int
    end: int
    text: str


def iter_files() -> Iterator[pathlib.Path]:
    """Iterate over all documentation files with supported extensions."""
    exts = {".md", ".txt", ".yml", ".yaml"}
    for p in DOC_DIR.rglob("*"):
        if p.suffix.lower() in exts and p.is_file():
            yield p


def chunk_text(text: str) -> Sequence[str]:
    """
    Split text into overlapping chunks.

    This is a naive char-based chunking. For Markdown,
    splitting on headings might be more effective.
    """
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + CHUNK_SIZE])
        i += CHUNK_SIZE - OVERLAP
    return chunks


def build_index() -> None:
    """
    Build and save the vector index for all documentation files.
    Uses scikit-learn's TfidfVectorizer and stores vectors with NumPy.
    """
    # Use scikit-learn's TfidfVectorizer
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))

    metas: list[Dict[str, Any]] = []
    chunks: list[str] = []
    file_paths: list[str] = []

    for file in iter_files():
        content = file.read_text(encoding="utf-8", errors="ignore")
        file_path = str(file.relative_to(DOC_DIR))

        for i, chunk in enumerate(chunk_text(content)):
            chunks.append(chunk)
            file_paths.append(file_path)
            metas.append({"file": file_path, "text": chunk})

    # Fit and transform the chunks to create document vectors
    if not chunks:
        print("No documents found to index!")
        return

    matrix = vectorizer.fit_transform(chunks)
    matrix_dense: np.ndarray = matrix.toarray().astype("float32")

    # Normalize vectors for cosine similarity
    norms = np.linalg.norm(matrix_dense, axis=1, keepdims=True)
    # Avoid division by zero
    norms[norms == 0] = 1
    normalized_matrix = matrix_dense / norms

    # Save matrix to file
    np.save(str(INDEX_PATH), normalized_matrix)

    # Save vocabulary and idf values as JSON
    vocab_path = DOC_DIR / ".tfidf_vocab.json"
    with vocab_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "vocabulary": vectorizer.vocabulary_,
                "idf": vectorizer.idf_.tolist(),
            },
            f,
            ensure_ascii=False,
        )

    with META_PATH.open("w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
