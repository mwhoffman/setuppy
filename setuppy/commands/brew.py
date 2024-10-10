"""Implementation of the brew command."""

from dataclasses import dataclass
from typing import Any

from setuppy.commands.base import BaseCommand


@dataclass
class Brew(BaseCommand):
  """Implementation of the brew command."""
  packages: list[str]

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run a brew action."""
    # TODO: Fill in this stub command.
    return False
