"""Deprecated monolithic CLI – kept for backward compatibility."""

from __future__ import annotations

from importlib import import_module

# Runtime import so editable installs get latest code
_cli_pkg = import_module("mcp_simple_tool.cli.__init__")
main = _cli_pkg.main

if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main())
