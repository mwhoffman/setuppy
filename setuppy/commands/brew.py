"""Implementation of the brew command."""

from dataclasses import dataclass
from typing import Any

from setuppy.commands.command import Command


@dataclass
class Brew(Command):
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
    cmd = f"brew install {' '.join(packages)}"
    return False
