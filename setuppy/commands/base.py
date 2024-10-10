"""Base command class."""

import abc
import dataclasses
from typing import Any


@dataclasses.dataclass
class CommandResult:
  """Return value of a command."""
  changed: bool
  facts: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class BaseCommand(metaclass=abc.ABCMeta):
  """Base class for defining commands."""

  @abc.abstractmethod
  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the command."""
