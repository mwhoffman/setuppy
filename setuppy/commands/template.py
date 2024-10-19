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
  """Recursively format and write template files from `source` to `dest`.

  This command takes a `source` directory, recursively finds all files under
  this directory, and copies them to the directory `dest`. The contents of each
  source file is formatted using `str.format` with substitutions given by the
  global facts dictionary.

  The returned `CommandResult` will have `result.changed` set to `True` if a
  change is made, i.e. if any file under `source` is created under the `dest`.
  """
  source: str
  dest: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the template command."""
    source = pathlib.Path(self.source.format(**facts))
    dest = pathlib.Path(self.dest.format(**facts))
    changed = False

    # Raise an exception if source exists and is not a directory.
    if not source.is_dir():
      msg = f'"{source.absolute()}" does not exist or is not a directory.'
      raise SetuppyError(msg)

    # NOTE: In order to support py3.11 we can't use source.walk() which was only
    # introduced in py3.12.

    # Walk the path.
    for path, _, files in os.walk(source):
      for f in files:
        file = pathlib.Path(path) / f
        target = dest / file.relative_to(source)

        if target.exists():
          # Raise an exception if the target exists and is not a file.
          if target.is_dir():
            msg = f'"{target.absolute()}" exists and is not a file.'
            raise SetuppyError(msg)

          # Otherwise we'll just log and skip the target.
          logging.info('Target "%s" exists', target)
          continue

          # TODO: Should we try and evaluate whether the file's contents would
          # be changed and only skip if they WOULDN'T be changed.

        # Target doesn't exist so we'll create it.
        changed = True
        logging.info('Creating "%s"', target)

        # Ensure the target's parent dirs exist and run the command, but only if
        # we're not simulating.
        if not simulate:
          target.parent.mkdir(parents=True)
          target.write_text(file.read_text().format(**facts))

    return CommandResult(changed=changed)
