"""Implementation of the template command."""

import dataclasses
import logging
import pathlib
from typing import Any

import jinja2

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Template(BaseCommand):
  """Implementation of the template command."""
  source: str
  dest: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the command."""
    source = pathlib.Path(self.source.format(**facts))
    dest = pathlib.Path(self.dest.format(**facts))

    if not source.is_dir():
      msg = f'"{source.absolute()}" does not exist or is not a directory.'
      raise SetuppyError(msg)

    changed = False
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(source)))

    for subpath, _, files in source.walk():
      for file in files:
        dotfile = subpath.relative_to(source) / file
        target = dest / dotfile
        if target.exists():
          logging.info('Target "%s" exists', target)
        else:
          changed = True
          logging.info('Creating "%s"', target)
          if not simulate:
            template = env.get_template(str(dotfile))
            with target.open("w") as f:
              f.write(template.render(**facts))

    return CommandResult(changed=changed)
