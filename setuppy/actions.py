"""Actions."""

from typing import Callable

from setuppy.facts import Facts
from setuppy.logger import Logger


Actions: dict[str, Callable] = {}


def register(action: Callable) -> Callable:
  """Register an action."""
  Actions[action.__name__] = action
  return action


@register
def stow(
    facts: Facts,
    logger: Logger,
    simulate: bool,
    *,
    package: str,
) -> bool:
  """Run a stow action."""
  stowdir = "dotfiles"
  target = facts["home"]
  cmd = f"stow -v --no-folding -d {stowdir} -t {target} -R {package}"
  cmd += " -n" if simulate else ""
  logger.log(f"{cmd}", 2)

  return False


@register
def github(
    facts: Facts,
    logger: Logger,
    simulate: bool,
    *,
    dest: str,
    account: str,
    repo: str,
) -> bool:
  """Run a github action."""
  target = f"{facts['home']}/{dest}/{repo}"
  url = f"https://github.com/{account}/{repo}"
  cmd = f"git clone {url} {target}"
  logger.log(f"{cmd}", 2)

  return False
