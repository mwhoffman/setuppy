"""Implementation of the github command."""

import os
from dataclasses import dataclass
from typing import Any

import click

from setuppy.commands.command import Command


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
    verbosity: int,
  ) -> tuple[bool, str]:
    """Run a github action."""
    dest = self.dest.format(**facts)

    for source in self.sources:
      source = source.format(**facts)
      url = f"https://github.com/{source}"
      target = f"{dest}/{os.path.basename(source)}"
      cmd = f"git clone {url} {target}"

      if verbosity >= 4:
        click.echo(f"    {cmd}")

      return False, ""
