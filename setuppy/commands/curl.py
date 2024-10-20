"""Implementation of the curl command."""

import dataclasses
import logging
import os
import pathlib
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_pipe
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Curl(BaseCommand):
  """Run curl to download and explode a tarball.

  This command takes a collection of `sources`, i.e. a list of urls, and will
  use curl to download them and expand/untar them into the given `dest`
  directory. The exact target directory will be `dest/basename` where basename
  is the base name of the source url (i.e. without its suffix). The suffix of
  the source is used to determine how to expand it. Currently this onyl supports
  files of the form `.tar.xz`.

  The returned `CommandResult` will have `result.changed` set to `True` if a
  change is made, i.e. if the target directory doesn't already exist.
  """
  sources: list[str]
  dest: str

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the curl command."""
    dest = pathlib.Path(self.dest.format(**facts))
    changed = False

    for s in self.sources:
      source = s.format(**facts)
      target = dest / os.path.basename(source)
      suffix = "".join(target.suffixes)

      # Find the unsuffixed name and based on the suffix save the option to pass
      # to tar to expand the tarball.
      match suffix:
        case ".tar.xz":
          taropt = "J"
          target = target.with_suffix("").with_suffix("")
        case _:
          # Or raise an exception if we don't know what to do.
          raise SetuppyError('Unknown suffix "{suffix}"')

      if target.exists():
        # Raise an exception if the target exists and is a file.
        if target.is_file():
          raise SetuppyError('Target "%s" exist and is a file', target)

        # Otherwise it's a directory so we'll skip it.
        logging.info('Target "%s" exists', target)
        continue

      # Target doesn't exist so we'll create it.
      changed = True
      cmd1 = ["curl", "-sSL", source]
      cmd2 = ["tar", f"-x{taropt}f", "-", "-C", str(target)]
      logging.info('Running command "%s | %s"', " ".join(cmd1), " ".join(cmd2))

      # Ensure the target dir exists and run the command, but only if we're not
      # simulating.
      if not simulate:
        target.mkdir(parents=True, exist_ok=True)
        rc, _, _ = run_pipe(cmd1, cmd2)
        if rc != 0:
          msg = f'Error downloading target "{target}".'
          raise SetuppyError(msg)

    return CommandResult(changed)
