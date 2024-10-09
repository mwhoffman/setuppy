"""Command line interface for setup."""

import sys

import click
from dataclass_binder import Binder

from setuppy.commands.command import CommandError
from setuppy.controller import Controller
from setuppy.types import Recipe


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
  tags: list[str],
  simulate: bool,
  verbosity: int,
):
  """Run setup for the given TAGS."""

  # Instantiate the controller.
  controller = Controller(
    tags=tags,
    simulate=simulate,
    verbosity=verbosity,
  )

  try:
    recipes = [Binder(Recipe).parse_toml(filename) for filename in filenames]
    controller.run(recipes)

  except CommandError as e:
    click.secho(str(e), fg="red")
    sys.exit(-1)


if __name__ == "__main__":
  main()
