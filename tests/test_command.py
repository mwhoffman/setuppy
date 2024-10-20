"""Test for the raw "command" command."""

from collections.abc import Iterable
from unittest import mock

import pytest

from setuppy.commands.command import Command
from setuppy.types import SetuppyError


@pytest.fixture
def run_command() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.command.run_command")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


def test_command(run_command: mock.MagicMock):
  # Make sure we call the command.
  command = Command("ls")
  rv = command(facts={}, simulate=False)
  assert rv.changed
  assert run_command.called
  run_command.assert_called_with("ls")


def test_command_simulate(run_command: mock.MagicMock):
  # Same as above, but we simulate so make sure the command is not called.
  command = Command("ls")
  rv = command(facts={}, simulate=True)
  assert rv.changed
  assert not run_command.called


def test_command_fails(run_command: mock.MagicMock):
  # Same as above, but the command fails so we should raise an exception.
  command = Command("ls")
  run_command.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    command(facts={}, simulate=False)
