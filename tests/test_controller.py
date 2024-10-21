"""Tests for the controller class."""

import dataclasses
from typing import Any
from typing import TypedDict
from unittest import mock

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
  raises: bool = False

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run a command that does nothing."""
    del facts
    del simulate
    if self.raises:
      raise RuntimeError
    return CommandResult(changed=self.changed)


class ControllerKwargs(TypedDict):
  """Typed kwargs for a controller."""
  recipes: list[types.Recipe]
  tags: list[str]
  variables: dict[str, Any]
  config: types.Config
  force_all_tags: bool
  simulate: bool
  verbosity: int


# Basic set of kwargs we'll override in the tests below.
KWARGS = ControllerKwargs(
  recipes=[],
  tags=[],
  variables={},
  config=types.Config(),
  force_all_tags=False,
  simulate=False,
  verbosity=0,
)

def test_init_controller():
  # Initialize an empty controller.
  Controller(**KWARGS)

  # Try to force all tags.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(force_all_tags=True)
  Controller(**kwargs_)

  # Raise an exception if we pass a system tag.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(tags=["macos"])
  with pytest.raises(types.SetuppyError):
    Controller(**kwargs_)

  # Raise an exception if we pass unknown tags.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(tags=["foo"])
  with pytest.raises(types.SetuppyError):
    Controller(**kwargs_)

  # Raise an exception if we try to pass tags and force all tags.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(tags=["foo"], force_all_tags=True)
  with pytest.raises(types.SetuppyError):
    Controller(**kwargs_)

  # Raise an exception if we're missing variables.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(config=types.Config(required_variables=["foo", "bar"]))
  with pytest.raises(types.SetuppyError):
    Controller(**kwargs_)


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

  invalid_action = types.Action(name="foo", kind="bar")
  error_action = types.Action(name="foo", kind="noop", kwargs={"raises": True})

  # Run a basic controller with no verbosity.
  kwargs_ = ControllerKwargs(**KWARGS)
  kwargs_.update(recipes=recipes)
  controller = Controller(**kwargs_)
  controller.run()

  # Raise an exception if we run an invalid action.
  with pytest.raises(types.SetuppyError):
    controller._run_action(invalid_action)

  # Raise an exception if the action raises an exception.
  with pytest.raises(RuntimeError):
    controller._run_action(error_action)

  # Run the same with all the verbosity.
  kwargs_.update(verbosity=3)
  controller = Controller(**kwargs_)
  controller.run()

  # Raise an exception if we run an invalid action.
  with pytest.raises(types.SetuppyError):
    controller._run_action(invalid_action)

  # Raise an exception if the action raises an exception.
  with pytest.raises(RuntimeError):
    controller._run_action(error_action)


def test_facts():
  with mock.patch("os.uname") as uname:
    uname.return_value = mock.MagicMock(spec=["sysname"])
    uname.return_value.sysname = "Linux"
    assert "linux" in Controller(**KWARGS).tags

  with mock.patch("os.uname") as uname:
    uname.return_value = mock.MagicMock(spec=["sysname"])
    uname.return_value.sysname = "Darwin"
    assert "macos" in Controller(**KWARGS).tags

  with mock.patch("os.uname") as uname:
    uname.return_value = mock.MagicMock(spec=["sysname"])
    uname.return_value.sysname = "foobarbaz"
    with pytest.raises(types.SetuppyError):
      Controller(**KWARGS)
