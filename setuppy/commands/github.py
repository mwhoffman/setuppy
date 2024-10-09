"""Implementation of the github command."""

import dataclasses
import logging
import os
import pathlib
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Github(BaseCommand):
  """Implementation of the stow command."""
  sources: list[str]
  dest: str

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run a github action."""
    dest = pathlib.Path(self.dest.format(**facts))
    changed = False

    for s in self.sources:
      source = s.format(**facts)
      target = dest / os.path.basename(source)
      url = f"https://github.com/{source}"

      if target.exists():
        if not target.is_dir():
          msg = f'Target "{target}" exists and is not a directory.'
          raise SetuppyError(msg)

        gitdir = target / ".git"
        if gitdir.exists() and not gitdir.is_dir():
          msg = f'Target "{target}" exists and is not a git directory.'
          raise SetuppyError(msg)

        cmd = f"git --git-dir={gitdir} remote get-url origin"
        rc, stderr, _ = run_command(cmd)

        if rc != 0:
          msg = f'Error accessing git-dir "{gitdir}".'
          raise SetuppyError(msg)

        if stderr.strip() != url:
          msg = (
            f'Target "{target}" exists, but tracks a different upstream '
            'repository.'
          )
          raise SetuppyError(msg)

        # The target must be a git directory pointed at the correct repository.
        logging.info('Target "%s" exists', target)
        continue

      changed = True
      cmd = f"git clone {url} {target}"

      if simulate:
        logging.info('Skipping command "%s"', cmd)
        continue

      rc, stderr, _ = run_command(cmd)

      if rc != 0:
        msg = f'Error cloning target "{target}".'
        raise SetuppyError(msg)

    return changed
