"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from mcp_simple_tool.cli import (
    cli,
    get_server_pid,
    is_process_running,
    is_server_running,
)


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


def test_is_server_running_success():
    """Test the is_server_running function when server responds."""
    # given
    mock_response = MagicMock()
    mock_response.status_code = 200

    # when/then
    with patch("requests.head", return_value=mock_response) as mock_head:
        assert is_server_running(7000) is True
        mock_head.assert_called_once_with("http://localhost:7000/sse", timeout=(1, 2))


def test_is_server_running_failure():
    """Test the is_server_running function when server doesn't respond."""
    # given
    from requests.exceptions import RequestException

    # when/then
    with patch("requests.head", side_effect=RequestException()) as mock_head:
        assert is_server_running(7000) is False
        mock_head.assert_called_once_with("http://localhost:7000/sse", timeout=(1, 2))


def test_is_process_running_true():
    """Test is_process_running when process exists."""
    # given/when
    with patch("os.kill") as mock_kill:
        # then
        assert is_process_running(1234) is True
        mock_kill.assert_called_once_with(1234, 0)


def test_is_process_running_false():
    """Test is_process_running when process doesn't exist."""
    # given

    # when/then
    with patch("os.kill", side_effect=OSError()) as mock_kill:
        assert is_process_running(1234) is False
        mock_kill.assert_called_once_with(1234, 0)


def test_get_server_pid_found():
    """Test get_server_pid when process is found."""
    # given
    mock_output = (
        "COMMAND  PID USER   FD TYPE DEVICE SIZE/OFF NODE NAME\n"
        "Python  1234 user  7u IPv4 12345 0t0 TCP *:7000 (LISTEN)"
    )

    # when/then
    with patch(
        "subprocess.check_output", return_value=mock_output.encode("utf-8")
    ) as mock_check:
        pid = get_server_pid(7000)
        assert pid == 1234
        mock_check.assert_called_once_with(["lsof", "-i", ":7000", "-sTCP:LISTEN"])


def test_get_server_pid_not_found():
    """Test get_server_pid when process is not found."""
    # given
    from subprocess import SubprocessError

    # when/then
    with patch("subprocess.check_output", side_effect=SubprocessError()) as mock_check:
        assert get_server_pid(7000) is None
        mock_check.assert_called_once_with(["lsof", "-i", ":7000", "-sTCP:LISTEN"])


def test_cli_help(runner):
    """Test the CLI help command."""
    # when
    result = runner.invoke(cli, ["--help"])

    # then
    assert result.exit_code == 0
    assert "check" in result.output
    assert "restart" in result.output
    assert "start" in result.output
    assert "stop" in result.output


def test_start_command_server_already_running(runner):
    """Test start command when server is already running."""
    # given/when
    with patch("mcp_simple_tool.cli.is_server_running", return_value=True):
        result = runner.invoke(cli, ["start"])

    # then
    assert result.exit_code == 0
    assert "already running" in result.output


def test_start_command_port_in_use(runner):
    """Test start command when port is in use but server is not responding."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
    ):
        result = runner.invoke(cli, ["start"])

    # then
    assert result.exit_code != 0
    assert "already in use" in result.output


def test_check_command_server_running(runner):
    """Test check command when server is running."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=True),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
    ):
        result = runner.invoke(cli, ["check"])

    # then
    assert result.exit_code == 0
    assert "Server process found with PID: 1234" in result.output
    assert "Server is up and running" in result.output


def test_check_command_server_not_running(runner):
    """Test check command when server is not running."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=None),
    ):
        result = runner.invoke(cli, ["check"])

    # then
    assert result.exit_code != 0
    assert "No server process found" in result.output


def test_stop_command_server_running(runner):
    """Test stop command when server is running."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
        patch("mcp_simple_tool.cli.is_process_running", side_effect=[True, False]),
        patch("os.kill") as mock_kill,
        patch("time.sleep"),
    ):
        result = runner.invoke(cli, ["stop"])

    # then
    assert result.exit_code == 0
    assert "Found server process: 1234" in result.output
    assert "Server terminated successfully" in result.output
    mock_kill.assert_called_with(1234, 15)  # SIGTERM


def test_stop_command_force_kill(runner):
    """Test stop command with force flag."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
        patch("mcp_simple_tool.cli.is_process_running", return_value=False),
        patch("os.kill") as mock_kill,
        patch("time.sleep"),
    ):
        result = runner.invoke(cli, ["stop", "--force"])

    # then
    assert result.exit_code == 0
    assert "Found server process: 1234" in result.output
    assert "Server terminated successfully with force kill" in result.output
    mock_kill.assert_called_with(1234, 9)  # SIGKILL


def test_stop_command_server_not_running(runner):
    """Test stop command when server is not running."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.get_server_pid", return_value=None),
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
    ):
        result = runner.invoke(cli, ["stop"])

    # then
    assert result.exit_code == 0
    assert "No server found running" in result.output


def test_restart_command_server_running(runner):
    """Test restart command when server is already running."""
    # given
    with (
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
        patch("mcp_simple_tool.cli.is_server_running", return_value=True),
        patch("mcp_simple_tool.cli.stop") as mock_stop,
        patch("socket.socket") as mock_socket,
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
    ):
        # Mock socket bind method
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance

        # when
        runner.invoke(cli, ["restart"])

    # then
    assert mock_stop.callback.called
    assert mock_socket.called
    assert mock_sock_instance.bind.called
    assert mock_popen.called


def test_start_command_daemon_mode(runner):
    """Test start command in daemon mode."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=None),
        patch("subprocess.Popen") as mock_popen,
    ):
        result = runner.invoke(cli, ["start", "--daemon"])

    # then
    assert result.exit_code == 0
    assert "Server started in background mode" in result.output
    assert mock_popen.called


def test_start_command_foreground(runner):
    """Test start command in foreground mode."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=None),
        patch("uvicorn.run") as mock_run,
    ):
        # This will run until uvicorn exits
        result = runner.invoke(cli, ["start"])

    # then
    assert "Starting MCP website fetcher server on port" in result.output
    assert mock_run.called


def test_check_command_process_running_not_responding(runner):
    """Test check command when process is running but not responding."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.is_server_running", return_value=False),
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
    ):
        result = runner.invoke(cli, ["check"])

    # then
    assert result.exit_code != 0
    assert "Server process found with PID: 1234" in result.output
    assert "not responding properly" in result.output


def test_stop_command_process_not_terminating(runner):
    """Test stop command when process doesn't terminate gracefully."""
    # given/when
    with (
        patch("mcp_simple_tool.cli.get_server_pid", return_value=1234),
        patch("mcp_simple_tool.cli.is_process_running", return_value=True),
        patch("os.kill") as mock_kill,
        patch("time.sleep"),
    ):
        result = runner.invoke(cli, ["stop"])

    # then
    assert result.exit_code != 0
    assert "Failed to kill server process" in result.output
    assert mock_kill.call_count >= 2  # SIGTERM and SIGKILL
