"""Setup controller."""

from typing import Callable

from setuppy.facts import get_facts
from setuppy.logger import Logger
from setuppy.recipe import Recipe
from setuppy.recipe import Tags


ACTION_MAPPING: dict[str, Callable] = {}


def register(action: Callable) -> Callable:
  """Register an action."""
  ACTION_MAPPING[action.__name__] = action
  return action


class Controller:
  """A controller for running setup tasks."""

  def __init__(self, *, tags: Tags, simulate: bool, verbosity: int):
    """Initialize the controller.

    Args:
      tags: a set of tags to enable.
      simulate: if true, simulate all commands.
      verbosity: how verbose to be.
    """
    self.simulate = simulate
    self.logger = Logger(verbosity)
    self.tags = set(tags)
    self.facts = get_facts()

    self.logger.log("Initializing setup...", 1)
    self.logger.log("Gathering facts...", 1)
    for name, value in sorted(self.facts.items()):
      self.logger.indent().log(f"{name}: {value}", 2)

    match self.facts["uname"]:
      case "Linux":
        self.tags.add("linux")
      case "Darwin":
        self.tags.add("macos")

    self.logger.indent().log(f"tags: {", ".join(self.tags)}", 2)

  def run(self, recipe: Recipe):
    """Run the given recipe."""

    if not recipe.tags.issubset(self.tags):
      self.logger.log(f'Skipping recipe "{recipe.name}"...', 3)
      return

    self.logger.log(f'Running recipe "{recipe.name}"...', 1)

    for action in recipe.actions:
      if not action.tags.issubset(self.tags):
        self.logger.indent().log("Skipping action...", 3)
        continue

      kwarg_str = ", ".join(f"{k}={v}" for (k, v) in action.kwargs.items())
      self.logger.indent().log(f"{action.kind}({kwarg_str})", 3)

  def stow(self, package: str) -> bool:
    """Run a stow action."""
    stowdir = "dotfiles"
    target = self.facts["home"]
    cmd = f"stow -v --no-folding -d {stowdir} -t {target} -R {package}"
    cmd += " -n" if self.simulate else ""
    self.logger.indent().log(f"{cmd}", 2)

    return False

  def github(self, dest: str, account: str, repo: str) -> bool:
    """Run a github action."""
    target = f"{self.facts['home']}/{dest}/{repo}"
    url = f"https://github.com/{account}/{repo}"
    cmd = f"git clone {url} {target}"
    self.logger.indent().log(f"{cmd}", 2)

    return False
