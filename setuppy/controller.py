"""Setup controller."""

from setuppy.actions import Actions
from setuppy.facts import get_facts
from setuppy.logger import Logger
from setuppy.recipe import Action
from setuppy.recipe import Recipe
from setuppy.recipe import Tags


class Controller:
  """A controller for running setup tasks."""

  def __init__(
    self,
    *,
    tags: Tags,
    simulate: bool,
    verbosity: int,
    logger: Logger | None = None,
  ):
    """Initialize the controller.

    Args:
      tags: a set of tags to enable.
      simulate: if true, simulate all commands.
      verbosity: how verbose to be.
    """
    self.simulate = simulate
    self.logger = logger or Logger(verbosity)
    self.tags = set(tags)
    self.facts = get_facts()

    logger = self.logger
    logger.log("Initializing setup...", 1)
    logger.log("Gathering facts...", 1)

    logger = logger.indent()
    for name, value in sorted(self.facts.items()):
      logger.log(f"{name}: {value}", 2)

    match self.facts["uname"]:
      case "Linux":
        self.tags.add("linux")
      case "Darwin":
        self.tags.add("macos")

    logger.log(f"tags: {", ".join(self.tags)}", 2)

  def should_skip(self, tags: Tags) -> bool:
    return not tags.issubset(self.tags)

  def run(
    self,
    recipe: Recipe,
    logger: Logger | None = None,
  ):
    """Run the given recipe."""

    if logger is None:
      logger = self.logger

    skipped = self.should_skip(recipe.tags)
    logger.log(f'Running recipe "{recipe.name}"...', 1, skipped=skipped)

    if skipped:
      return

    for action in recipe.actions:
      self.run_action(action, logger.indent())

  def run_action(
    self,
    action: Action,
    logger: Logger | None = None,
  ):
    """Run the given action."""
    if logger is None:
      logger = self.logger

    kwarg_str = ", ".join(f"{k}={v}" for (k, v) in action.kwargs.items())
    skipped = self.should_skip(action.tags)
    logger.log(f"{action.kind}({kwarg_str})", 3, skipped=skipped)

    if skipped:
      return

    if action.kind in Actions:
      Actions[action.kind](
        self.facts,
        logger.indent(),
        self.simulate,
        **action.kwargs,
      )
