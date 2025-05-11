from __future__ import annotations

import pathlib
from typing import List

import mcp.types as types
from pydantic import BaseModel, Field, field_validator

# Constants
DOC_ROOT = pathlib.Path(__file__).resolve().parents[2] / "docs"
ALLOWED_EXTS = {".md", ".txt", ".yml", ".yaml"}
CHUNK_SIZE = 1_000  # characters


class DocPath(BaseModel):
    """Validated, normalised path relative to docs root."""

    file: str = Field(..., description="Relative path inside docs")

    @field_validator("file")
    def _safe_path(cls, v: str) -> str:
        if ".." in pathlib.Path(v).parts:
            raise ValueError("Parent traversal not allowed")
        if pathlib.Path(v).suffix.lower() not in ALLOWED_EXTS:
            raise ValueError("Unsupported extension")
        full = DOC_ROOT / v
        if not full.is_file():
            raise FileNotFoundError(f"{v} not found")
        return v


def read_local_doc(rel_path: str) -> List[types.TextContent]:
    """Return file content chunked into TextContent objects."""
    validated = DocPath(file=rel_path).file
    text = (DOC_ROOT / validated).read_text(encoding="utf-8", errors="ignore")
    # Chunk to stay within typical LLM context windows
    chunks = [
        types.TextContent(type="text", text=text[i : i + CHUNK_SIZE])
        for i in range(0, len(text), CHUNK_SIZE)
    ]
    return chunks
