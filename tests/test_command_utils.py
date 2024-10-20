"""Test for the command running utilities."""

import dataclasses
import subprocess
from unittest import mock

import pytest

from setuppy.commands import utils
from setuppy.types import SetuppyError


@dataclasses.dataclass
class MockProcessRV:
  """Mock for the return value of subprocess.run."""
  returncode: int
  stdout: str
  stderr: str

  def communicate(self) -> tuple[str, str]:
    """Mock communicate function for subprocess.Popen."""
    return "", ""


@mock.patch("subprocess.run")
@mock.patch("shutil.which")
def test_run_command(
  which: mock.MagicMock,
  run: mock.MagicMock,
):
  # "Command" we'll run.
  path = "ls"
  args = ["foo", "bar", "baz"]
  cmd = [path, *args]
  fullpath = "/bin/ls"

  # Should raise an exception if which can't find the right command.
  which.return_value = None
  with pytest.raises(SetuppyError):
    utils.run_command(cmd)
  which.assert_called_once_with(path)

  # Setup the mocks for run_command.
  which.return_value = fullpath
  run.return_value = MockProcessRV(0, "", "")

  # The expected kwargs to call subprocess.run with.
  run_kwargs = dict(capture_output=True, encoding="utf-8", check=False)

  # Call run_command.
  run.reset_mock()
  utils.run_command(cmd)
  run.assert_called_once_with([fullpath, *args], **run_kwargs)

  # Call run_command with sudo.
  run.reset_mock()
  utils.run_command(cmd, sudo=True)
  run.assert_called_once_with(["/usr/bin/sudo", fullpath, *args], **run_kwargs)


@mock.patch("subprocess.Popen")
@mock.patch("shutil.which")
def test_run_pipe(
  which: mock.MagicMock,
  popen: mock.MagicMock,
):
  cmd1 = ["ls", "foo", "bar", "baz"]
  cmd2 = ["cat"]
  fullcmd1 = ["/bin/ls", *cmd1[1:]]
  fullcmd2 = ["/usr/bin/cat"]

  # Raise an exception if the first cmd can't be found.
  which.return_value = None
  with pytest.raises(SetuppyError):
    utils.run_pipe(cmd1, cmd2)
  assert which.call_count == 1
  which.assert_any_call("ls")

  # Raise an exception if the second cmd can't be found.
  which.reset_mock(return_value=True)
  which.side_effect = [fullcmd1[0], None]
  with pytest.raises(SetuppyError):
    utils.run_pipe(cmd1, cmd2)
  assert which.call_count == 2
  which.assert_any_call("ls")
  which.assert_any_call("cat")

  # Run the two piped processes and verify we properly call Popen.
  which.reset_mock(return_value=True)
  which.side_effect = [fullcmd1[0], fullcmd2[0]]
  popen.return_value = MockProcessRV(0, "stdout", "stderr")
  utils.run_pipe(cmd1, cmd2)
  assert popen.call_count == 2
  popen.assert_any_call(fullcmd1, stdout=subprocess.PIPE)
  popen.assert_any_call(
    fullcmd2, stdin="stdout", stdout=subprocess.PIPE, encoding="utf-8"
  )
