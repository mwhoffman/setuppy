"""Setup controller."""

import logging
import os
from typing import Any

import click

from setuppy.commands import CommandRegistry
from setuppy.commands.command import CommandError
from setuppy.types import Action
from setuppy.types import Recipe


def get_facts() -> dict[str, Any]:
  """Get basic system facts."""
  facts = dict()
  facts["home"] = os.getenv("HOME")
  facts["user"] = os.getenv("USER")
  facts["cwd"] = os.getcwd()
  facts["uname"] = os.uname().sysname
  return facts


class Controller:
  """A controller for running setup tasks."""

  def __init__(
    self,
    *,
    tags: list[str],
    simulate: bool,
    verbosity: int,
  ):
    """Initialize the controller.

    Args:
      tags: a set of tags to enable.
      simulate: if true, simulate all commands.
      verbosity: how verbose to be.
    """
    self.simulate = simulate
    self.verbosity = verbosity
    self.tags = set(tags)
    self.facts = get_facts()

    if self.verbosity >= 1:
      click.echo("Initializing setup...")

    match self.facts["uname"]:
      case "Linux":
        self.tags.add("linux")
      case "Darwin":
        self.tags.add("macos")

  def should_skip(self, tags: list[str]) -> bool:
    """Evaluate whether an action should be skipped.

    Returns true if an action associated with the given tags should be
    skipped.
    """
    return not set(tags).issubset(self.tags)

  def run(self, recipes: list[Recipe] | Recipe):
    """Run the given recipes."""
    recipes = recipes if isinstance(recipes, list) else [recipes]
    for recipe in recipes:
      self.run_recipe(recipe)

  def run_recipe(self, recipe: Recipe):
    """Run the given recipe."""
    # Output message for the recipe.
    msg = f"Running recipe: {recipe.name}"

    if self.should_skip(recipe.tags):
      logging.info('Skipping recipe "%s"', recipe.name)
      if self.verbosity >= 2:
        click.echo(msg + click.style(" [skipped]", fg="yellow"))
      return

    logging.info('Running recipe "%s"', recipe.name)
    if self.verbosity >= 1:
      click.echo(msg)

    for action in recipe.actions:
      self.run_action(action)

  def run_action(self, action: Action):
    """Run the given action."""
    # Output message for the action.
    msg = f"  {action.name}..."

    # Skip; output a message if verbosity is high enough (otherwise we're just
    # silent).
    if self.should_skip(action.tags):
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
      raise CommandError('unknown action kind "{action.kind}"')

    command = CommandRegistry[action.kind](**action.kwargs)

    try:
      changed = command(facts=self.facts, simulate=self.simulate)

    except Exception:
      if self.verbosity >= 1:
        # Mark the status before reraising.
        click.secho(" [error]", fg="red")
      raise

    # Mark the status of the command.
    if self.verbosity >= 1:
      if changed:
        click.secho(" [changed]", fg="yellow")
      else:
        click.secho(" [ok]", fg="green")
