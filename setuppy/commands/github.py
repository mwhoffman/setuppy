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
      gitdir = target / ".git"
      url = f"https://github.com/{source}"

      if target.exists():
        # Raise an exception if the target is not a proper gitdir.
        if not target.is_dir() or not gitdir.exists() or not gitdir.is_dir():
          msg = f'Target "{target}" exists and is not a git directory.'
          raise SetuppyError(msg)

        # Run a git command to get the remote origin.
        cmd = ["git", "--git-dir", str(gitdir), "remote", "get-url", "origin"]
        logging.info('Running command "%s"', " ".join(cmd))
        rc, stderr, _ = run_command(cmd)

        # Raise an exception if the command returns an error.
        if rc != 0:
          msg = f'error accessing git-dir "{gitdir}".'
          raise SetuppyError(msg)

        # Raise an exception if the origin is wrong.
        if stderr.strip() != url:
          msg = f'target "{target}" exists, but tracks a different repository.'
          raise SetuppyError(msg)

        # The target must be a git directory pointed at the correct repository
        # so we'll skip this target.
        logging.info('Target "%s" exists', target)
        continue

      # Otherwise we should run the git command to clone the repository.
      changed = True
      cmd = ["git", "clone", url, str(target)]
      logging.info('Running command "%s"', " ".join(cmd))

      # Run the git command if we're not simulating.
      if not simulate:
        rc, stderr, _ = run_command(cmd)
        if rc != 0:
          msg = f'Error cloning target "{target}".'
          raise SetuppyError(msg)

    return CommandResult(changed)
