"""Implementation of a basic shell command."""

import dataclasses
import logging
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Command(BaseCommand):
  """Run a basic shell command.

  This command runs a basic shell command passed as a string. Because we don't
  know anything else about the command this will always return
  `CommandResult.changed` set to True.
  """
  command: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run a raw command."""
    cmd = [c.format(**facts) for c in self.command]
    logging.info('Running command "%s"', " ".join(cmd))

    if not simulate:
      rc, _, _ = run_command(cmd)
      if rc != 0:
        msg = f'Error running command "{' '.join(cmd)}".'
        raise SetuppyError(msg)

    return CommandResult(changed=True)
