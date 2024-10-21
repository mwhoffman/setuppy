"""Tests for the controller class."""

import dataclasses
from typing import Any

import pytest

from setuppy import types
from setuppy.commands import register
from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.controller import Controller


# Register a noop command so we can use it in a recipe.
@register
@dataclasses.dataclass
class Noop(BaseCommand):
  """Command that does nothing."""
  changed: bool = False

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run a command that does nothing."""
    del facts
    del simulate
    return CommandResult(changed=self.changed)


def test_init_controller():
  # Initialize an empty controller.
  Controller(
    recipes=[],
    tags=[],
    variables={},
    config=types.Config(),
    force_all_tags=True,
    simulate=False,
    verbosity=0,
  )

  # Raise an exception if we try to pass tags and force all tags.
  with pytest.raises(types.SetuppyError):
    Controller(
      recipes=[],
      tags=["foo"],
      variables={},
      config=types.Config(),
      force_all_tags=True,
      simulate=False,
      verbosity=0,
    )

  # Raise an exception if we're missing variables.
  with pytest.raises(types.SetuppyError):
    Controller(
      recipes=[],
      tags=[],
      variables={},
      config=types.Config(required_variables=["foo", "bar"]),
      force_all_tags=False,
      simulate=False,
      verbosity=0,
    )


def test_run_controller():
  actions = [
    types.Action(name="noop1", kind="noop", register="foo"),
    types.Action(name="noop2", kind="noop", parents=["foo"]),
    types.Action(name="noop3", kind="noop", tags=["foo"]),
    types.Action(name="noop4", kind="noop", kwargs={"changed": True}),
  ]
  recipes = [
    types.Recipe(name="noop1", actions=actions),
    types.Recipe(name="noop2", actions=[], tags=["foo"]),
  ]

  # Run a basic controller with no verbosity.
  Controller(
    recipes=recipes,
    tags=[],
    variables={},
    config=types.Config(),
    force_all_tags=False,
    simulate=False,
    verbosity=0,
  ).run()

  # Run the same with all the verbosity.
  Controller(
    recipes=recipes,
    tags=[],
    variables={},
    config=types.Config(),
    force_all_tags=False,
    simulate=False,
    verbosity=3,
  ).run()
