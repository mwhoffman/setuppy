"""Implementation of the brew command."""

import dataclasses
import logging
import shlex
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Brew(BaseCommand):
  """Run brew to install a collection of packages.

  This command uses brew to install the given collection of packages. It will
  first check what packages are installed, skipping this step if
  `facts["brew_packages"]` exists containing a cached list of installed
  packages. It will then attempt to install those requested packages that are
  missing.

  The returned `CommandResult` will have `result.changed` set to `True` if any
  packages were installed, and `result.facts["brew_packages"]` will correspond
  to a list of those packages installed after this command has run.
  """
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run a brew action."""
    # Try and get a cached list of packages.
    installed = facts.get("brew_packages")

    # Get the installed packages if they're not cached.
    if installed is None:
      # Find formula.
      rc, stderr, _ = run_command(r"brew list --formula -1")
      if rc != 0:
        raise SetuppyError("Error determining installed packages.")
      installed = stderr.strip().split()

      # Find casks.
      rc, stderr, _ = run_command(r"brew list --cask -1")
      if rc != 0:
        raise SetuppyError("Error determining installed packages.")
      installed.extend(stderr.strip().split())

    packages = [p.format(**facts) for p in self.packages]
    packages = list(set(packages).difference(set(installed)))

    installed.extend(packages)
    facts = {"brew_packages": installed}

    # If packages is empty then nothing will change.
    if not packages:
      return CommandResult(changed=False, facts=facts)

    # Construct the command.
    packages = [shlex.quote(p) for p in packages]
    cmd = f"brew install {' '.join(packages)}"

    if simulate:
      logging.info('Skipping command "%s"', cmd)
    else:
      rc, _, _ = run_command(cmd)
      if rc != 0:
        msg = f'Error running command "{cmd}".'
        raise SetuppyError(msg)

    return CommandResult(changed=True, facts=facts)
