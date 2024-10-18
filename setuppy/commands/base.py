"""Base command class."""

import abc
import dataclasses
from typing import Any


@dataclasses.dataclass
class CommandResult:
  """Return value of a command.

  Properties:
    changed: whether the command caused a change to the system.
    facts: any updates to the system facts determined by the command.
  """
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
    """Run the command.

    Args:
      facts: a dictionary containing system facts.
      simulate: whether to simulate the command or not.

    Returns:
      A `CommandResult` whose `changed` field indicates whether the command
      caused a change in the system. The `facts` dictionary contains updated
      system facts which can be used by the caller to update the global
      collection of facts.
    """
