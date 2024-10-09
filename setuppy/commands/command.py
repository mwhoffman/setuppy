"""Base command class."""

import shlex
import shutil
import subprocess
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Command(metaclass=ABCMeta):
  """Command base class."""

  @abstractmethod
  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run the command."""


class CommandError(RuntimeError):
  """Error raised within setuppy."""


def run_command(cmd: str) -> tuple[int, str, str]:
  """Run the given command.

  Args:
    cmd: the command and its arguments to run.

  Returns:
    A tuple (rc, stdout, stderr) containing the return code of the command and
    stdout and stderr as strings.
  """
  args = shlex.split(cmd)
  path = shutil.which(args[0])

  if path is None:
    raise CommandError(f"Could not find command: {path}")

  args[0] = path

  p = subprocess.run(args, capture_output=True, encoding="utf-8", check=False)
  return p.returncode, p.stdout, p.stderr
