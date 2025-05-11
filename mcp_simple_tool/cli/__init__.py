"""Public entry-point for `python -m mcp_simple_tool` & `mcp-simple-tool`."""

from __future__ import annotations

import click

# Re-export utility functions for backward compatibility
from .utils import get_server_pid, is_process_running, is_server_running  # noqa: F401


# Create CLI group
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:  # pragma: no cover
    """MCP Simple Tool command-line interface."""
    pass


# Import and add command functions to the CLI group
from .check_cmd import check  # noqa: E402
from .restart_cmd import restart  # noqa: E402
from .start_cmd import start  # noqa: E402
from .stop_cmd import stop  # noqa: E402

# Add commands to the CLI group
cli.add_command(check)
cli.add_command(restart)
cli.add_command(start)
cli.add_command(stop)


# Expose legacy `main()` so old imports still work
def main() -> int:  # pragma: no cover
    """Backward-compat shim for `mcp_simple_tool.cli:main`."""
    cli()  # Click processes `sys.argv`
    return 0


# Re-export for `python -m mcp_simple_tool`
if __name__ == "__main__":  # pragma: no cover
    main()


# Define exported symbols
__all__ = [
    "cli",
    "main",
    # re-exported utils (for tests relying on dotted path)
    "is_server_running",
    "get_server_pid",
    "is_process_running",
]
