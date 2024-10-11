"""Command line interface for setup."""

import logging
import pathlib
import sys

import click
from dataclass_binder import Binder

from setuppy.controller import Controller
from setuppy.types import Recipe
from setuppy.types import SetuppyError


"""Setup command line wrapper."""
@click.command
@click.option(
  "-t",
  "tags",
  metavar="TAG",
  multiple=True,
  help=(
    "Include the given TAG; can be specified multiple times to include "
    "multiple tags."
  ),
)
@click.option(
  "-r",
  "recipedir",
  metavar="RECIPEDIR",
  default="recipes",
  help='Directory to search for recipes in. Defaults to "recipes".',
)
@click.option(
  "-n",
  "simulate",
  is_flag=True,
  help="Do nothing, i.e. simulate the tasks, but making no changes.",
)
@click.option(
  "-v",
  "verbosity",
  count=True,
  help="Verbose; multiple flags increases verbosity.",
)
@click.option(
  "--log-to-stdout",
  "log_to_stdout",
  is_flag=True,
  help="Verbosely log to stdout (ignores the verbosity flag).",
)
def main(
  *,
  tags: tuple[str],
  recipedir: str,
  simulate: bool,
  verbosity: int,
  log_to_stdout: bool,
):
  """Run setup for the given recipes.

  This will collect the recipes it finds in RECIPEDIR and run setup for the
  associated actions. Tags can be specified with `-t TAG` to decide which
  recipes and subsequent actions to include. A recipe or action will only be run
  if all of its tags are specified.
  """

  # Set our logging level.
  if log_to_stdout:
    verbosity = 0
    logging.basicConfig(level=logging.DEBUG)

  # Instantiate the controller.
  controller = Controller(
    tags=list(tags),
    simulate=simulate,
    verbosity=verbosity,
  )

  try:
    filenames = list(pathlib.Path(recipedir).glob("*.toml"))
    recipes = [Binder(Recipe).parse_toml(filename) for filename in filenames]
    controller.run(recipes)

  except SetuppyError as e:
    click.secho(str(e), fg="red")
    sys.exit(-1)


if __name__ == "__main__":
  main()
