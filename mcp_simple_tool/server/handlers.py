"""MCP tool handlers."""

from __future__ import annotations

from typing import Annotated, List

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from mcp_simple_tool.semantic_search.search import semantic_search
from mcp_simple_tool.server.doc_reader import read_local_doc

from .config import Settings
from .http import fetch

settings = Settings()
mcp = FastMCP("mcp-website-fetcher-sse")


@mcp.tool(
    description="Fetch a remote web page over HTTP and return its full text.",
)
async def http_fetch_tool(
    url: Annotated[str, Field(description="Absolute HTTP/HTTPS URL to retrieve")],
) -> Annotated[
    List[types.TextContent],
    Field(
        description=(
            "Single‑element list where the only TextContent item contains the raw "
            "response body as plain text."
        )
    ),
]:
    """Fetch a URL via HTTP (uses server‑side network access).

    The returned list always has exactly one TextContent object whose ``text`` field
    is the full response body.
    """
    content = await fetch(url, headers={"User-Agent": settings.user_agent})
    return [types.TextContent(type="text", text=content)]


@mcp.tool(
    description=(
        "Semantic search across documentation from ``docs`` folder "
        "and return the top‑k excerpts."
    ),
)
async def search_docs_tool(
    query: Annotated[
        str, Field(description="Search phrase or question to look up in the docs")
    ],
    k: Annotated[
        int,
        Field(
            description="Number of top matches to return (1–20)",
            ge=1,
            le=20,
        ),
    ] = 3,
) -> Annotated[
    List[types.TextContent],
    Field(
        description=(
            "Each TextContent item contains a formatted excerpt with the file path, "
            "similarity score, and a snippet separated by an HR."
        )
    ),
]:
    """Perform a semantic search over local documentation.

    Returns a pretty‑formatted excerpt for each match so the agent can decide which
    file to read in full with ``get_local_content_tool``.
    """
    results = semantic_search(query, k)

    contents: List[types.TextContent] = []
    for r in results:
        pretty = (
            f"**{r['file']}**  (score {r['score']:.3f})\n\n"
            f"{r['excerpt'].strip()}\n\n---\n"
        )
        contents.append(types.TextContent(type="text", text=pretty))
    return contents


@mcp.tool(
    description="Return the full contents of a local documentation file.",
)
async def get_local_content_tool(
    file: Annotated[
        str,
        Field(
            description=(
                "Relative path inside ``mcp_python_sdk_docs``: "
                "e.g. ``core-concepts/server.md``"
            )
        ),
    ],
) -> Annotated[
    List[types.TextContent],
    Field(
        description=(
            "The file split into ≈1 000‑character TextContent chunks, in order. "
            "Concatenate ``text`` fields to reconstruct the original file."
        )
    ),
]:
    """Load the entire markdown / YAML / text document from the local docs folder.

    Use this after ``search_docs_tool`` to read a file that was referenced in the
    search results.
    """
    return read_local_doc(file)
