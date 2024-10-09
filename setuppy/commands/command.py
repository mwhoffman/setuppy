"""Base command class."""

import shlex
import shutil
import subprocess

from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

import click


@dataclass
class Command(metaclass=ABCMeta):
  """Command base class."""

  @abstractmethod
  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
    verbosity: int,
  ) -> tuple[bool, str]:
    """Run the command."""


class CommandError(RuntimeError):
  pass


def run_command(cmd: str, verbosity: int) -> tuple[int, str, str]:
  args = shlex.split(cmd)
  path = shutil.which(args[0])

  if path is None:
    raise CommandError(f"Could not find command: {path}")

  args[0] = path

  if verbosity >= 4:
    click.echo(f"    {' '.join(args)}")

  p = subprocess.run(args, capture_output=True, encoding="utf-8")
  return p.returncode, p.stdout, p.stderr
