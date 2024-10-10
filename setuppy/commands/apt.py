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
  """Implementation of the apt command."""
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run an apt action."""
    # Try and get a cached list of packages.
    installed = facts.get("apt_packages")

    # Get the installed packages if they're not cached.
    if installed is None:
      rc, stderr, _ = run_command(r"dpkg-query -f '${binary:Package}\n' -W")
      if rc != 0:
        raise SetuppyError("Error determining installed packages.")
      installed = stderr.strip().split()

    packages = [p.format(**facts) for p in self.packages]
    packages = list(set(packages).difference(set(installed)))

    installed.extend(packages)
    facts = {"apt_packages": installed}

    # If packages is empty then nothing will change.
    if not packages:
      return CommandResult(changed=False, facts=facts)

    # Construct the command.
    packages = [shlex.quote(p) for p in packages]
    cmd = f"apt-get -y install {' '.join(packages)}"

    if simulate:
      logging.info('Skipping command "sudo %s"', cmd)
    else:
      rc, _, _ = run_command(cmd, sudo=True)
      if rc != 0:
        msg = f'Error running command "{cmd}".'
        raise SetuppyError(msg)

    return CommandResult(changed=True, facts=facts)
