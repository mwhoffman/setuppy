"""Recipe and Action data structures."""

from dataclasses import dataclass
from typing import Any


type Tags = set[str]
type Parents = set[str]


@dataclass
class Action:
  """Action data structure."""
  kind: str
  name: str | None
  parents: Parents
  tags: Tags
  kwargs: dict[str, Any]

  @classmethod
  def from_dict(cls, kwargs: dict[str, Any]) -> "Action":
    """Construct an Action from its dictionary representation."""
    kind: str = kwargs.pop("kind")
    name = kwargs.pop("name", None)
    parents: Parents = set(kwargs.pop("parents", ()))
    tags: Tags = set(kwargs.pop("tags", ()))

    # TODO: check that we've parsed the entire entry.

    return cls(
      kind=kind,
      name=name,
      parents=parents,
      tags=tags,
      kwargs=kwargs
    )


@dataclass
class Recipe:
  """Recipe data structure."""
  name: str
  tags: Tags
  actions: list[Action]

  @classmethod
  def from_dict(cls, kwargs: dict[str, Any]) -> "Recipe":
    """Construct a Recipe from its dictionary representation."""
    name: str = kwargs.pop("name")
    tags: Tags = set(kwargs.pop("tags", ()))
    actions = [Action.from_dict(a) for a in kwargs.pop("action", [])]

    # TODO: check that we've parsed the entire entry.

    return cls(
      name=name,
      tags=tags,
      actions=actions,
    )
