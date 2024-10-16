"""Implementation of the github command."""

import dataclasses
import logging
import os
import pathlib
import shlex
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Github(BaseCommand):
  """Clone repositories from github into the destination directory.

  This command takes a collection of `sources`, i.e. a list github repositories
  of the form "user/repository" and will use `git` to clone those sources into
  the destination directory `dest`.

  The returned `CommandResult` will have `result.changed` set to `True` if a
  change is made, i.e. if the target didn't already exist and was created.
  """
  sources: list[str]
  dest: str

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the github action."""
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

        cmd = f"git --git-dir={shlex.quote(str(gitdir))} remote get-url origin"
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
      cmd = f"git clone {shlex.quote(url)} {shlex.quote(str(target))}"

      if simulate:
        logging.info('Skipping command "%s"', cmd)
      else:
        rc, stderr, _ = run_command(cmd)
        if rc != 0:
          msg = f'Error cloning target "{target}".'
          raise SetuppyError(msg)

    return CommandResult(changed)
