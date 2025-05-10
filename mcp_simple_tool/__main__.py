"""Main entrypoint for the MCP Simple Tool."""

import sys

from mcp_simple_tool.cli import main

# Always call main() to make it easier to test
if __name__ == "__main__":
    sys.exit(main())
else:
    # For testing purposes, still call main but don't exit
    main()
