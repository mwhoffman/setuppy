"""Implementation of the stow command."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from setuppy.commands.command import Command
from setuppy.commands.command import CommandError
from setuppy.commands.command import run_command


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


def get_conflicts_from_stderr(stderr: str, version: str) -> set[str]:
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


def get_changes_from_stderr(stderr: str) -> tuple[set[str], set[str]]:
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


@dataclass
class Stow(Command):
  """Implementation of the stow command."""
  package: str
  stowdir: str = "dotfiles"
  target: str = "{home}"

  def __call__(
    self,
    *,
    facts: dict[str, Any],
    simulate: bool,
  ) -> bool:
    """Run the command."""
    # Get the version of stow.
    rc, stdout, _ = run_command("stow --version")
    if rc != 0:
      raise CommandError("Could not get stow version")

    match = re.match(
      r"^stow \(GNU Stow\) version (?P<version>\d+\.\d+\.\d+)$",
      stdout.strip())

    if not match:
      raise CommandError("Could not parse stow version")

    version = match.group("version")

    if version not in STOW_CONFLICT_RE:
      raise CommandError(f'Unsupported stow version "{version}"')

    # Format the input options.
    package = self.package.format(**facts)
    stowdir = self.stowdir.format(**facts)
    target = self.target.format(**facts)

    if not Path(stowdir).exists():
      msg = f'stowdir "{stowdir}" does not exist'
      raise CommandError(msg)

    if not (Path(stowdir) / package).exists():
      msg = f'package directory "{stowdir}/{package}" does not exist'
      raise CommandError(msg)

    # Format the command itself.
    cmd = f"stow -v --no-folding -d {stowdir} -t {target} -R {package}"
    cmd += " -n" if simulate else ""

    # Run the command. If rc is nonzero there should be conflicts which we can
    # identify and mark as a failure.
    rc, _, stderr = run_command(cmd)
    if rc != 0:
      conflicts = get_conflicts_from_stderr(stderr, version)
      conflicts = ", ".join(conflicts)
      raise CommandError(f"Conflicting targets: {conflicts}")

    # Otherwise we can find the links that were either removed or added. If any
    # were this counts as a change.
    unlinked, linked = get_changes_from_stderr(stderr)
    changed = bool(linked | unlinked)

    # Format the message.
    msg = ""
    for name, files in (("unlinked", unlinked), ("linked", linked)):
      if files:
        msg = msg + "; " if msg else ""
        msg = msg + f"{name}: " + ", ".join(files)

    return changed
