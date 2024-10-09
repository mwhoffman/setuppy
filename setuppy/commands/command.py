"""Base command class."""

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
  ):
    """Run the command."""


def has_command(cmd: str, verbosity: int) -> bool:
  rc, _, _ = run_command(f"which {cmd}", verbosity)
  return rc == 0


def run_command(cmd: str, verbosity: int) -> tuple[int, str, str]:
  if verbosity >= 4:
    click.echo(f"    {cmd}")
  # FIXME: Actually implement this.
  return 0, "", ""
