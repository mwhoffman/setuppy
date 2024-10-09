"""Setup controller."""

import os
from typing import Any

import click

from setuppy.commands import CommandRegistry
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
      click.echo("Gathering facts...")

    if self.verbosity >= 4:
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
    msg = click.style("Running recipe: ")
    msg += click.style(recipe.name, underline=True)
    skip = self.should_skip(recipe.tags)

    if skip:
      if self.verbosity >= 3:
        click.echo(msg, nl=False)
        click.secho(" [skipped]", fg="yellow")
      return

    if self.verbosity >= 1:
      click.echo(msg)

    for action in recipe.actions:
      self.run_action(action)

  def run_action(self, action: Action):
    """Run the given action."""
    msg = click.style(f"  {action.name}...")
    skip = self.should_skip(action.tags)

    if skip:
      if self.verbosity >= 3:
        click.echo(msg, nl=False)
        click.secho(" [skipped]", fg="yellow")
      return

    if self.verbosity >= 2:
      click.echo(msg)

    if action.kind in CommandRegistry:
      command = CommandRegistry[action.kind](**action.kwargs)
      command(
        facts=self.facts,
        simulate=self.simulate,
        verbosity=self.verbosity,
      )
