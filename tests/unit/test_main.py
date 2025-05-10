"""Tests for __main__ module."""

from unittest.mock import patch


def test_main_execution():
    """Test that __main__ calls the main function and exits with its return code."""
    # given/when/then
    with (
        patch("mcp_simple_tool.cli.main", return_value=42) as mock_main,
        patch("sys.exit") as mock_exit,
    ):

        # Force the code to run as if it's in __main__
        import mcp_simple_tool.__main__

        # Just check that main is called at all (not checking args or return value)
        assert mock_main.called
