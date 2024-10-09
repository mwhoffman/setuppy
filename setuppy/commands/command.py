"""Base command class."""

from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any


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
