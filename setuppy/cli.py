"""Command line interface for setup."""

import logging
import os
import pathlib
import sys

import click
import dataclass_binder
import tomllib

from setuppy.controller import Controller
from setuppy.types import Config
from setuppy.types import Recipe
from setuppy.types import SetuppyError


"""Setup command line wrapper."""
@click.command
@click.option(
  "-t",
  "tags",
  metavar="TAG",
  multiple=True,
  help="Include the given TAG.",
)
@click.option(
  "-a",
  "force_all_tags",
  is_flag=True,
  help="Include all tags; ignores -t.",
)
@click.option(
  "-d",
  "basedir",
  metavar="BASEDIR",
  help="Set the base working directory.",
)
@click.option(
  "-n",
  "simulate",
  is_flag=True,
  help="Do nothing; simulate actions, but make no changes.",
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
  help="Verbosely log to stdout; ignores -v.",
)
def main(
  *,
  tags: tuple[str],
  force_all_tags: bool,
  basedir: str | None,
  simulate: bool,
  verbosity: int,
  log_to_stdout: bool,
) -> int:
  """Search for setup recipes and run them.

  Which actions are run is controlled by passing tags to setup. Tags can be
  specified with the `-t TAG` option and can be passed multiple times to select
  multiple tags. A recipe or action will only be run if all of its tags are
  specified.

  Recipes consist of .toml files and will be searched for in BASEDIR/recipes/.
  If BASEDIR is not specified this will default to the same directory as the
  setup script itself (or "." if the setuppy module is called directly).

  Note that any relative path specified in a recipe is taken to be relative to
  BASEDIR.
  """
  # Set our logging level.
  if log_to_stdout:
    verbosity = 0
    logging.basicConfig(level=logging.DEBUG)

  # Find the default config directory. If we're running under "-m setuppy.cli"
  # (i.e. this module) we'll default to "."; otherwise we'll set it based on
  # whatever directory is running the main script (which we get from argv).
  if not basedir:
    if __name__ == "__main__":
      basedir = "."
    else:
      basedir = str(pathlib.Path(sys.argv[0]).parent)

  # Make sure the config directory exists.
  basepath = pathlib.Path(basedir)
  if not basepath.is_dir():
    msg = f'could not find config directory "{basepath.absolute()}"'
    click.secho(f"Error: {msg}", fg="red")
    return -1

  # Change directory so that from now on everything is relative to basedir.
  os.chdir(basepath)

  # Make sure the recipe directory exists.
  recipepath = pathlib.Path("recipes")
  if not recipepath.is_dir():
    msg = f'could not find recipe directory "{recipepath.absolute()}"'
    click.secho(f"Error: {msg}", fg="red")
    return -1

  # Gather variables if they exist.
  variablepath = pathlib.Path("variables.toml")
  if variablepath.is_file():
    with variablepath.open("rb") as f:
      variables = tomllib.load(f)
  else:
    variables = {}

  # Gather variables if they exist.
  configpath = pathlib.Path("config.toml")
  if configpath.is_file():
    config = dataclass_binder.Binder(Config).parse_toml(configpath)
  else:
    config = Config()

  # TODO: catch Binder errors.
  recipes = [
    dataclass_binder.Binder(Recipe).parse_toml(filename)
    for filename in list(recipepath.glob("*.toml"))
  ]

  try:
    # Instantiate and run the controller.
    Controller(
      recipes=recipes,
      tags=list(tags),
      variables=variables,
      config=config,
      force_all_tags=force_all_tags,
      simulate=simulate,
      verbosity=verbosity,
    ).run()

  except SetuppyError as e:
    click.secho(f"Error: {e}", fg="red")
    return -1

  return 0


if __name__ == "__main__":
  sys.exit(main())
