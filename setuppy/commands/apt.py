"""Implementation of the apt command."""

from dataclasses import dataclass
from typing import Any

from setuppy.commands.base import BaseCommand


@dataclass
class Apt(BaseCommand):
  """Implementation of the brew command."""
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run a github action."""
    packages = [p.format(**facts) for p in self.packages]
    cmd = f"sudo apt-get install {' '.join(packages)}"
    return False
