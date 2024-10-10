"""Implementation of a basic command."""

import dataclasses
import logging
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Command(BaseCommand):
  """Implementation of a basic command."""
  command: str

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run a basic command."""
    cmd = self.command.format(**facts)

    if simulate:
      logging.info('Skipping command "%s"', cmd)
      return True

    # NOTE: this does not use shlex.quote because it may contain a command with
    # multiple terms.
    rc, _, _ = run_command(cmd)
    if rc != 0:
      msg = f'Error running command "{cmd}".'
      raise SetuppyError(msg)

    return True
