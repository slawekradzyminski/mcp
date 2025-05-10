"""Search functionality for semantic document search."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .indexing import INDEX_PATH, META_PATH, build_index


@lru_cache(maxsize=1)
def _load_assets() -> Tuple[TfidfVectorizer, np.ndarray, List[Dict[str, Any]]]:
    """
    Load or build search assets on first call.

    Returns:
        A tuple of (vectorizer, matrix, metadata)
    """
    # Build lazily if index missing
    if not INDEX_PATH.exists():
        build_index()

    # Load the TF-IDF vocabulary and IDF values
    vocab_path = INDEX_PATH.parent / ".tfidf_vocab.json"
    with vocab_path.open("r", encoding="utf-8") as f:
        tfidf_data = json.load(f)

    # Recreate the vectorizer
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    vectorizer.vocabulary_ = tfidf_data["vocabulary"]
    vectorizer.idf_ = np.array(tfidf_data["idf"])

    # Load normalized document vectors
    matrix = np.load(str(INDEX_PATH))

    meta: List[Dict[str, Any]] = [
        json.loads(line) for line in META_PATH.read_text().splitlines()
    ]
    return vectorizer, matrix, meta


def _cosine_similarity_search(matrix: np.ndarray, vec: np.ndarray, k: int) -> List[Tuple[int, float]]:
    """
    Perform k-nearest neighbors search using cosine similarity.

    Args:
        matrix: Matrix of document vectors (should be normalized)
        vec: Query vector
        k: Number of neighbors to return

    Returns:
        List of (index, score) tuples sorted by descending score
    """
    # Normalize the query vector
    vec_norm = np.linalg.norm(vec)
    if vec_norm > 0:
        vec = vec / vec_norm

    # Calculate cosine similarity (dot product of normalized vectors)
    sims = matrix @ vec
    
    # Get top k results
    k = min(k, len(sims))
    idxs = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in idxs]


def semantic_search(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Search for documents semantically similar to the query.

    Args:
        query: Search query text
        k: Number of top matches to return

    Returns:
        List of dicts with 'file', 'score', and 'excerpt' keys
    """
    vectorizer, matrix, meta = _load_assets()
    
    # Transform the query using the fitted vectorizer
    q_vec_sparse = vectorizer.transform([query])
    q_vec: np.ndarray = q_vec_sparse.toarray()[0].astype("float32")

    # Find similar documents using cosine similarity
    results = _cosine_similarity_search(matrix, q_vec, k)

    out: List[Dict[str, Any]] = []
    for idx, score in results:
        if idx < len(meta):  # Make sure index is valid
            m = meta[idx]
            out.append(
                {
                    "file": m["file"],
                    "score": score,
                    "excerpt": m["text"],
                }
            )

    return out
