#!/usr/bin/env python
"""CLI helper to manually rebuild the documentation search index."""

from mcp_simple_tool.semantic_search.indexing import build_index

if __name__ == "__main__":
    print("Building semantic-search index...")
    build_index()
    print("Done ✓") 