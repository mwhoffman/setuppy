"""Implementation of the template command."""

import dataclasses
import logging
import os
import pathlib
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Template(BaseCommand):
  """Implementation of the template command."""
  source: str
  dest: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the command."""
    source = pathlib.Path(self.source.format(**facts))
    dest = pathlib.Path(self.dest.format(**facts))

    if not source.is_dir():
      msg = f'"{source.absolute()}" does not exist or is not a directory.'
      raise SetuppyError(msg)

    changed = False
    for path, _, files in os.walk(source):
      for f in files:
        file = pathlib.Path(path) / f
        target = dest / file.relative_to(source)

        if target.exists():
          logging.info('Target "%s" exists', target)

        else:
          changed = True
          logging.info('Creating "%s"', target)
          if not simulate:
            target.write_text(file.read_text().format(**facts))

    return CommandResult(changed=changed)
