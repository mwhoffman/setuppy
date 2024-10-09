"""Implementation of the stow command."""

from dataclasses import dataclass
from typing import Any

import click

from setuppy.commands.command import Command


@dataclass
class Stow(Command):
  """Implementation of the stow command."""
  package: str
  stowdir: str = "dotfiles"
  target: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
    verbosity: int,
  ):
    """Run the command."""
    package = self.package.format(**facts)
    stowdir = self.stowdir.format(**facts)
    target = self.target.format(**facts)

    cmd = f"stow -v --no-folding -d {stowdir} -t {target} -R {package}"
    cmd += " -n" if simulate else ""

    if verbosity >= 4:
      click.echo(f"    {cmd}")
