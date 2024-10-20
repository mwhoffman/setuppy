"""Implementation of the stow command."""

# The implementation of this command drew initial inspiriation for the conflict
# checks from https://github.com/caian-org/ansible-stow, particularly with
# respect to the regex used, which follows the example given in that earlier
# code.

import dataclasses
import logging
import pathlib
import re
from typing import Any

from setuppy.commands.base import BaseCommand
from setuppy.commands.base import CommandResult
from setuppy.commands.utils import run_command
from setuppy.types import SetuppyError


# Define how to find conflicts based on stow's error message. This is version
# dependent, so we'll match the output of particular versions.
STOW_CONFLICT_RE = {
  "2.3.1": (
    r"^\* existing target is neither a link nor a directory: "
    r"(?P<target>.+)$"
  ),
  "2.4.0": (
    r"^\* cannot stow (?P<src>.+) over existing target (?P<target>.+) "
    r"since neither a link nor a directory and --adopt not specified$"
  )
}

# Copy the message for matching versions.
STOW_CONFLICT_RE["2.4.1"] = STOW_CONFLICT_RE["2.4.0"]


@dataclasses.dataclass
class Stow(BaseCommand):
  """Implementation of the stow command."""
  package: str
  stowdir: str = "dotfiles"
  targetdir: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> CommandResult:
    """Run the command."""
    # Get the version of stow.
    version = facts.get("stow_version")

    if not version:
      version = _get_stow_version()

    # Format the input options.
    package = self.package.format(**facts)
    stowdir = pathlib.Path(self.stowdir.format(**facts))
    targetdir = pathlib.Path(self.targetdir.format(**facts))

    if not stowdir.is_dir():
      msg = f'stowdir "{stowdir}" does not exist or is not a directory.'
      raise SetuppyError(msg)

    if not (stowdir / package).is_dir():
      msg = f'package directory "{stowdir/package}" does not exist '
      msg += "or is not a directory."
      raise SetuppyError(msg)

    # Format the command itself.
    cmd = ["stow", "-v", "--no-folding"]
    cmd += ["-d", str(stowdir)]
    cmd += ["-t", str(targetdir)]
    cmd += ["-R", str(package)]
    cmd += ["-n"] if simulate else []

    # Run the command. If rc is nonzero there should be conflicts which we can
    # identify and mark as a failure.
    rc, _, stderr = run_command(cmd)
    if rc != 0:
      conflicts = _get_conflicts_from_stderr(stderr, version)
      conflicts = [f'"{targetdir/conflict}"' for conflict in conflicts]
      msg = f"target files already exist: {', '.join(conflicts)}"
      raise SetuppyError(msg)

    # Otherwise we can find the links that were either removed or added.
    unlinked, linked = _get_changes_from_stderr(stderr)

    if unlinked:
      files = [f'"{targetdir/file}"' for file in unlinked]
      logging.info("Unlinking files %s", ", ".join(files))

    if linked:
      files = [f'"{targetdir/file}"' for file in linked]
      logging.info("Linking files %s", ", ".join(files))

    return CommandResult(
        changed=bool(linked | unlinked),
        facts={"stow_version": version},
    )


def _get_stow_version() -> str:
  """Get the version of stow."""
  rc, stdout, _ = run_command(["stow", "--version"])
  if rc != 0:
    raise SetuppyError("could not get stow version.")

  match = re.match(
    r"^stow \(GNU Stow\) version (?P<version>\d+\.\d+\.\d+)$",
    stdout.strip())

  if not match:
    raise SetuppyError("could not parse stow version.")

  version = match.group("version")

  if version not in STOW_CONFLICT_RE:
    raise SetuppyError(f'unsupported stow version "{version}".')

  return version


def _get_conflicts_from_stderr(stderr: str, version: str) -> set[str]:
  """Parse the stderr returned by stow and find any conflicts.

  Args:
    stderr: the stderr (str) returned by running stow.
    version: the version of stow.

  Returns:
    A set of strings consisting of the conflicting files.
  """
  conflict_re = re.compile(STOW_CONFLICT_RE[version])
  conflicts = set()
  for line in stderr.split("\n"):
    match = conflict_re.match(line.strip())
    if match:
      conflicts.add(match.group("target"))
  return conflicts


def _get_changes_from_stderr(stderr: str) -> tuple[set[str], set[str]]:
  """Return the set of unlinked and linked changes.

  Args:
    stderr: the stderr (str) returned by running stow.

  Returns:
    Two sets of strings the first of which are the set of files that have been
    removed by stow and the second is the set of files that have been added by
    stow.
  """
  # Each line should contain info for a single file that was linked/unlinked. So
  # we will grab that using the following regexes.
  unlinked_re = re.compile(r"^UNLINK: (?P<target>.+)$")
  linked_re = re.compile(r"^LINK: (?P<target>.+) =>")

  # Build up these two sets.
  unlinked = set()
  linked = set()

  for line in stderr.split("\n"):
    match = unlinked_re.match(line.strip())
    if match:
      unlinked.add(match.group("target"))
      continue
    match = linked_re.match(line.strip())
    if match:
      linked.add(match.group("target"))

  return unlinked-linked, linked-unlinked
