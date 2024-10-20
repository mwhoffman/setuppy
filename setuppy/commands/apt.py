"""Implementation of the apt command."""

import dataclasses
import logging
import shlex
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_command
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Apt(BaseCommand):
  """Run apt-get to install a collection of packages.

  This command uses apt-get to install the given collection of packages. It will
  first check what packages are installed, skipping this step if
  `facts["apt_packages"]` exists containing a cached list of installed packages.
  It will then attempt to install those requested packages that are missing.

  The returned `CommandResult` will have `result.changed` set to `True` if any
  packages were installed, and `result.facts["apt_packages"]` will correspond
  to a list of those packages installed after this command has run.
  """
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the command or do nothing if simulate is True."""
    # Try and get a cached list of packages.
    installed = facts.get("apt_packages")
    changed = False

    # Get the installed packages if they're not cached.
    if installed is None:
      rc, stderr, _ = run_command(r"dpkg-query -f '${binary:Package}\n' -W")
      if rc != 0:
        raise SetuppyError("Error determining installed packages.")
      installed = stderr.strip().split()

    # Find the packages that are not installed.
    packages = [p.format(**facts) for p in self.packages]
    packages = list(set(packages).difference(set(installed)))

    # Add uninstalled packages in so that we can cache installed packages with
    # our return value.
    installed.extend(packages)
    facts = {"apt_packages": installed}

    if packages:
      # If there are any uninstalled packages then we'll run a command to
      # install them.
      changed = True
      packages = [shlex.quote(p) for p in packages]
      cmd = f"apt-get -y install {' '.join(packages)}"
      logging.info('Skipping command "%s"', cmd)

      if not simulate:
        rc, _, _ = run_command(cmd, sudo=True)
        if rc != 0:
          msg = f'Error running command "{cmd}".'
          raise SetuppyError(msg)

    return CommandResult(changed=changed, facts=facts)
