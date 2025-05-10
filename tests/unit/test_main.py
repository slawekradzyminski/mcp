"""Tests for __main__ module."""

from unittest.mock import MagicMock, patch


def test_main_execution():
    """Test that __main__ calls the main function and exits with its return code."""
    # given
    mock_main = MagicMock(return_value=42)

    # when/then
    with (
        patch.dict("sys.modules", {"mcp_simple_tool.cli": MagicMock(main=mock_main)}),
        patch("sys.exit") as mock_exit,
    ):

        # Import the module
        import importlib

        import mcp_simple_tool.__main__

        importlib.reload(mcp_simple_tool.__main__)

        # Assert that main was called and exit was called with its return value
        assert mock_main.called
        mock_exit.assert_called_with(42)
