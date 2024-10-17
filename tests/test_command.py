"""Test for the raw "command" command."""

from unittest.mock import patch

import pytest

from setuppy.commands.command import Command
from setuppy.types import SetuppyError


@patch("setuppy.commands.command.run_command")
def test_command(run_command):
  command = Command("ls")
  run_command.return_value = (0, "", "")

  # If simulating return changed but don't call the command.
  rv = command(facts={}, simulate=True)
  assert rv.changed
  assert not run_command.called

  # Call the command and return changed.
  rv = command(facts={}, simulate=False)
  assert rv.changed
  assert run_command.called
  run_command.assert_called_with("ls")

  # Should raise an exception if the command fails.
  run_command.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    rv = command(facts={}, simulate=False)

