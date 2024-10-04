"""Command line interface for setup."""

import click
import tomllib

from setuppy.controller import Controller
from setuppy.recipe import Recipe


"""Setup command line wrapper."""
@click.command
@click.argument("filenames", nargs=-1)
@click.option(
  "-t",
  "tags",
  multiple=True,
  help="Tags; can be specified multiple times.",
)
@click.option(
  "-n",
  "simulate",
  is_flag=True,
  help="Do nothing; simulate tasks and exit.",
)
@click.option(
  "-v",
  "verbosity",
  count=True,
  help="Verbose; multiple flags increases verbosity.",
)
def main(
  *,
  filenames: tuple[str],
  tags: tuple[str],
  simulate: bool,
  verbosity: int,
):
  """Run setup for the given TAGS."""

  # Instantiate the controller.
  controller = Controller(
    tags=set(tags),
    simulate=simulate,
    verbosity=verbosity,
  )

  recipes = []
  for filename in filenames:
    with open(filename, "rb") as f:
      recipes.append(Recipe.from_dict(tomllib.load(f)))

  for recipe in recipes:
    controller.run(recipe)


if __name__ == "__main__":
  main()
