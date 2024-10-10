"""Command line interface for setup."""

import logging
import sys

import click
from dataclass_binder import Binder

from setuppy.controller import Controller
from setuppy.types import Recipe
from setuppy.types import SetuppyError


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
@click.option(
  "--log-to-stdout",
  "log_to_stdout",
  is_flag=True,
  help="Log to stdout; ignores verbosity if set.",
)
def main(
  *,
  filenames: tuple[str],
  tags: tuple[str],
  simulate: bool,
  verbosity: int,
  log_to_stdout: bool,
):
  """Run setup for the given TAGS."""

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
    recipes = [Binder(Recipe).parse_toml(filename) for filename in filenames]
    controller.run(recipes)

  except SetuppyError as e:
    click.secho(str(e), fg="red")
    sys.exit(-1)


if __name__ == "__main__":
  main()
