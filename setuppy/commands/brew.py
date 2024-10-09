"""Implementation of the brew command."""

from dataclasses import dataclass
from typing import Any

import click

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
    verbosity: int,
  ):
    """Run a github action."""
    packages = [p.format(**facts) for p in self.packages]
    cmd = f"brew install {' '.join(packages)}"
    if verbosity >= 4:
      click.echo(f"    {cmd}")
