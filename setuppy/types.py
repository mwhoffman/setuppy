"""Datatypes."""

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class Action:
  """Action data structure."""
  name: str
  kind: str
  kwargs: dict[str, Any] = field(default_factory=dict)
  register: str | None = None
  parents: list[str] = field(default_factory=list)
  tags: list[str] = field(default_factory=list)


@dataclass
class Recipe:
  """Recipe data structure."""
  name: str
  actions: list[Action]
  priority: int = 0
  tags: list[str] = field(default_factory=list)


class SetuppyError(RuntimeError):
  """Error raised within setuppy."""
