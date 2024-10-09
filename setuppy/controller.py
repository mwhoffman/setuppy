"""Setup controller."""

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

    if self.verbosity >= 4:
      click.echo("Facts:")
      for name, value in sorted(self.facts.items()):
        click.echo(f"  {name}: {value}")

    match self.facts["uname"]:
      case "Linux":
        self.tags.add("linux")
      case "Darwin":
        self.tags.add("macos")

    if self.verbosity >= 4:
      click.echo(f"  tags: {", ".join(self.tags)}")

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
    msg = f"Running recipe: {recipe.name}"
    skip = self.should_skip(recipe.tags)

    if skip:
      if self.verbosity >= 3:
        click.echo(msg, nl=False)
        click.secho(" [skipped]", fg="yellow")
      return

    if self.verbosity >= 1:
      click.echo(msg)

    for action in recipe.actions:
      try:
        self.run_action(action)
      except CommandError as e:
        msg = f'Error while running "{action.name}" in recipe "{recipe.name}":'
        msg += f"\n  {e}"
        raise CommandError(msg) from e

  def run_action(self, action: Action):
    """Run the given action."""
    # The message we'll log.
    msg = f"  {action.name}..."

    # Skip; output a message if verbosity is high enough (otherwise we're just
    # silent).
    if self.should_skip(action.tags):
      if self.verbosity >= 3:
        click.echo(msg + click.style(" [skipped]", fg="cyan"))
      return

    # Echo the message. No newline so we can mark it as changed later.
    if self.verbosity >= 2:
      click.echo(msg, nl=False)

    # Add a newline if the verbosity is high enough because running the command
    # will generate output.
    if self.verbosity >= 4:
      click.echo()

    if action.kind not in CommandRegistry:
      raise CommandError('unknown action kind "{action.kind}"')

    command = CommandRegistry[action.kind](**action.kwargs)

    try:
      changed = command(
        facts=self.facts, simulate=self.simulate, verbosity=self.verbosity
      )

    except Exception:
      # If we're waiting to see if anything changed add a newline because we'll
      # exit early after reraising.
      if self.verbosity >= 2 and self.verbosity < 4:
        click.echo()
      raise

    # Mark the command as causing a change, or add a newline if nothing changed.
    if self.verbosity >= 2 and self.verbosity < 4:
      if changed:
        click.secho(" [changed]", fg="yellow")
      else:
        click.echo()

    # If the verbosity is high enough message with what changed.
    elif self.verbosity >= 4 and changed:
      click.secho(f"    [changed]", fg="yellow")
