"""Entry point for the MCP Simple Tool package."""

import sys

from .cli import main

print("Starting MCP website fetcher")
sys.exit(main())
