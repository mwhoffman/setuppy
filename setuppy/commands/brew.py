"""Implementation of the brew command."""

import dataclasses
import logging
import shlex
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandOutput


@dataclasses.dataclass
class Brew(BaseCommand):
  """Implementation of the brew command."""
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandOutput:
    """Run a brew action."""
    changed = False

    packages = [p.format(**facts) for p in self.packages]
    packages = [shlex.quote(p) for p in self.packages]
    cmd = f"brew install {' '.join(packages)}"

    if simulate:
      logging.info('Skipping command "%s"', cmd)
      return CommandOutput(changed)

    # TODO: Run the command.
    logging.info('Running command "%s"', cmd)

    return CommandOutput(changed)
