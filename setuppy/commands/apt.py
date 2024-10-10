"""Implementation of the apt command."""

from dataclasses import dataclass
from typing import Any

from setuppy.commands.base import BaseCommand


@dataclass
class Apt(BaseCommand):
  """Implementation of the apt command."""
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run an apt action."""
    # TODO: Fill in this stub command.
    return False
