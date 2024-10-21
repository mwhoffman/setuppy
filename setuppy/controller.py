"""Setup controller."""

import logging
import os
from collections.abc import Iterable
from typing import Any
from typing import cast

import click
import dataclass_binder

from setuppy.commands import CommandRegistry
from setuppy.types import Action
from setuppy.types import Config
from setuppy.types import Recipe
from setuppy.types import SetuppyError


MAX_MSG_LEN = 30
MAX_TAGMSG_LEN = 30
SYSTEM_TAGS = {"macos", "linux"}


class Controller:
  """A controller for running setup tasks."""

  def __init__(
    self,
    *,
    recipes: list[Recipe],
    tags: list[str],
    variables: dict[str, Any],
    config: Config,
    force_all_tags: bool,
    simulate: bool,
    verbosity: int,
  ):
    """Initialize the controller.

    Args:
      recipes: collection of recipes to run.
      tags: a set of tags to enable.
      variables: additional facts specified as variables.
      config: configuration options.
      force_all_tags: force all tags that exist in the given recipes.
      simulate: if true, simulate all commands.
      verbosity: how verbose to be.
    """
    # Find all tags specified in the recipes.
    all_tags = set()
    for recipe in recipes:
      all_tags |= set(recipe.tags)
      for action in recipe.actions:
        all_tags |= set(action.tags)

    # Remove any system tags.
    all_tags -= SYSTEM_TAGS

    # Set the tags if we're forcing them to be everything.
    if force_all_tags:
      if tags:
        msg = "cannot specify tags and force_all_tags at the same time."
        raise SetuppyError(msg)
      tags = list(all_tags)

    else:
      _error_if_tags(set(tags) & SYSTEM_TAGS, "disallowed system")
      _error_if_tags(set(tags) - all_tags, "unknown")

    self.simulate = simulate
    self.verbosity = verbosity
    self.facts, system_tags = _get_facts()
    self.recipes = recipes
    self.tags = set(tags + system_tags)
    self.registry: dict[str, bool] = dict()

    missing_variables = set(config.required_variables) - set(variables.keys())
    if missing_variables:
      msg = "missing required variable"
      msg += f"{'s' if len(missing_variables) > 0 else ''} "
      msg += ", ".join(f'"{v}"' for v in missing_variables) + ". "
      msg += 'Add them to "variables.toml".'
      raise SetuppyError(msg)

    # Add variables as additional facts.
    self.facts.update(variables)

  def run(self):
    """Run the given recipes."""
    # Sort the recipes based on priority; lowest comes first so negate it so
    # highest priority items come first.
    for recipe in sorted(self.recipes, key=lambda recipe: -recipe.priority):
      self._run_recipe(recipe)

  def _should_skip(self, tags: list[str], parents: list[str]) -> bool:
    """Evaluate whether an action should be skipped.

    Returns true if an action associated with the given tags should be skipped
    (i.e. the action's/recipe's tags are not a subset of the controller's tags)
    or if none of its parents have changed.
    """
    # Skip if we're missing any tags.
    if not set(tags).issubset(self.tags):
      return True

    # If we satisfy all the tags and are checking the status of no parents then
    # we shouldn't skip.
    if not parents:
      return False

    # Otherwise if none of our parents have changed we should skip. Note that if
    # a parent has not been registered it is assumed to have not changed.
    return not any(self.registry.get(parent, False) for parent in parents)

  def _run_recipe(self, recipe: Recipe):
    """Run the given recipe."""
    # Output message for the recipe.
    msg = f"Running recipe: {recipe.name}"
    msg += "." * (MAX_MSG_LEN - len(msg))

    if self.verbosity >= 3:
      tagmsg = " [" + ", ".join(recipe.tags) + "]"
      tagmsg += "." * (MAX_TAGMSG_LEN - len(tagmsg))
      msg += tagmsg

    if self._should_skip(recipe.tags, []):
      logging.info('Skipping recipe "%s"', recipe.name)
      if self.verbosity >= 2:
        click.echo(msg + click.style(" [skipped]", fg="cyan"))
      return

    logging.info('Running recipe "%s"', recipe.name)
    if self.verbosity >= 1:
      click.echo(msg)

    for action in recipe.actions:
      self._run_action(action)

  def _run_action(self, action: Action):
    """Run the given action."""
    # Output message for the action.
    msg = f"  {action.name}"
    msg = msg + "." * (MAX_MSG_LEN - len(msg))

    if self.verbosity >= 3:
      tagmsg = " [" + ", ".join(action.tags) + "]"
      tagmsg += "." * (MAX_TAGMSG_LEN - len(tagmsg))
      msg += tagmsg

    # Skip; output a message if verbosity is high enough (otherwise we're just
    # silent).
    if self._should_skip(action.tags, action.parents):
      logging.info('Skipping action "%s"', action.name)
      if self.verbosity >= 2:
        click.echo(msg + click.style(" [skipped]", fg="cyan"))
      return

    # Echo the message. No newline so we can mark its status later.
    logging.info('Running action "%s"', action.name)
    if self.verbosity >= 1:
      click.echo(msg, nl=False)

    if action.kind not in CommandRegistry:
      if self.verbosity >= 1:
        click.secho(" [error]", fg="red")
      raise SetuppyError(f'unknown action kind "{action.kind}"')

    # TODO: Catch an error if raised.
    binder = dataclass_binder.Binder(CommandRegistry[action.kind])
    command = binder.bind(action.kwargs)

    try:
      result = command(facts=self.facts, simulate=self.simulate)

      # Update the controller's facts with any facts set by the action.
      self.facts.update(**result.facts)

      # Register a change for downstream actions.
      if action.register:
        self.registry[action.register] = result.changed

    except Exception:
      if self.verbosity >= 1:
        # Mark the status before reraising.
        click.secho(" [error]", fg="red")
      raise

    # Mark the status of the command.
    if self.verbosity >= 1:
      if result.changed:
        click.secho(" [changed]", fg="yellow")
      else:
        click.secho(" [ok]", fg="green")


def _error_if_tags(tags: Iterable[str], descriptor: str):
  """Raise an error if tags is not empty."""
  if tags:
    msg_tags = [f'"{tag}"' for tag in tags]
    msg = (
      f'passed {descriptor} tag{"s" if len(msg_tags) > 1 else ""} '
      f'{", ".join(msg_tags)}.'
    )
    raise SetuppyError(msg)


def _get_facts() -> tuple[dict[str, Any], list[str]]:
  """Get basic system facts."""
  facts = dict()
  system_tags = list()

  facts["home"] = os.getenv("HOME")
  facts["user"] = os.getenv("USER")
  facts["cwd"] = os.getcwd()
  facts["uname"] = os.uname().sysname

  # Cast this so we can assume it's a string.
  home = cast(str, facts["home"])

  match facts["uname"]:
    case "Linux":
      facts["fontdir"] = f"{home}/.local/share/fonts"
      system_tags += ["linux"]

    case "Darwin":
      facts["fontdir"] = f"{home}/Library/Fonts"
      system_tags += ["macos"]

    case _:
      raise SetuppyError("unknown uname value")

  return facts, system_tags
