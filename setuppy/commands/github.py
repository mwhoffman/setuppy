"""Implementation of the github command."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from setuppy.commands.command import Command
from setuppy.commands.command import CommandError
from setuppy.commands.command import run_command


@dataclass
class Github(Command):
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
    dest = Path(self.dest.format(**facts))
    changed = False

    for s in self.sources:
      source = s.format(**facts)
      target = dest / os.path.basename(source)
      url = f"https://github.com/{source}"

      if target.exists():
        if not target.is_dir():
          msg = f'Target "{target}" exists and is not a directory.'
          raise CommandError(msg)

        gitdir = target / ".git"
        if gitdir.exists() and not gitdir.is_dir():
          msg = f'Target "{target}" exists and is not a git directory.'
          raise CommandError(msg)

        cmd = f"git --git-dir={gitdir} remote get-url origin"
        rc, stderr, _ = run_command(cmd)

        if rc != 0:
          msg = f'Error accessing git-dir "{gitdir}".'
          raise CommandError(msg)

        if stderr.strip() != url:
          msg = (
            f'Target "{target}" exists, but tracks a different upstream '
            'repository.'
          )
          raise CommandError(msg)

        # The target must be a git directory pointed at the correct repository.
        continue

      changed = True

      if simulate:
        continue

      cmd = f"git clone {url} {target}"
      rc, stderr, _ = run_command(cmd)

      if rc != 0:
        msg = f'Error cloning target "{target}".'
        raise CommandError(msg)

    return changed
