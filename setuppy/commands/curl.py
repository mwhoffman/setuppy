"""Implementation of the curl command."""

import dataclasses
import logging
import os
import pathlib
import shlex
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import run_pipe
from setuppy.types import SetuppyError


@dataclasses.dataclass
class Curl(BaseCommand):
  """Implementation of the curl command."""
  sources: list[str]
  dest: str

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run curl."""
    dest = pathlib.Path(self.dest.format(**facts))
    changed = False

    for s in self.sources:
      source = s.format(**facts)
      target = dest / os.path.basename(source)
      suffix = "".join(target.suffixes)

      if suffix == ".tar.xz":
        taropt = "J"
        target = target.with_suffix("").with_suffix("")
      else:
        raise SetuppyError('Unknown suffix "{suffix}"')

      if target.exists() and target.is_dir():
        logging.info('Target "%s" exists', target)
        continue

      changed = True
      cmd1 = f"curl -sSL {shlex.quote(source)}"
      cmd2 = f"tar -x{taropt}f - -C {shlex.quote(str(target))}"

      if simulate:
        logging.info('Skipping command "%s | %s"', cmd1, cmd2)
        continue

      target.mkdir(parents=True, exist_ok=True)
      rc, _, _ = run_pipe(cmd1, cmd2)

      if rc != 0:
        msg = f'Error downloading target "{target}".'
        raise SetuppyError(msg)

    return changed
