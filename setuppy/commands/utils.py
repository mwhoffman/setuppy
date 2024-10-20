"""Utility functions for running commands."""

import logging
import shutil
import subprocess
from collections.abc import Iterable

from setuppy.types import SetuppyError


def run_command(
  cmd: Iterable[str],
  *,
  sudo: bool = False,
) -> tuple[int, str, str]:
  """Run the given command.

  Args:
    cmd: the command and its arguments to run.
    sudo: if true run the command under sudo.

  Returns:
    A tuple (rc, stdout, stderr) containing the return code of the command and
    stdout and stderr as strings.
  """
  cmd = list(cmd)
  fullpath = shutil.which(cmd[0])

  if fullpath is None:
    raise SetuppyError(f"Could not find command: {cmd[0]}")

  cmd[0] = fullpath

  if sudo:
    cmd = ["/usr/bin/sudo", *cmd]

  proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False)
  return proc.returncode, proc.stdout, proc.stderr


def run_pipe(
  cmd1: Iterable[str],
  cmd2: Iterable[str],
) -> tuple[int, str, str]:
  """Run the given command.

  Args:
    cmd1: the command and its arguments to run.
    cmd2: optional command to pipe the first into.

  Returns:
    A tuple (rc, stdout, stderr) containing the return code of the command and
    stdout and stderr as strings.
  """
  cmd1 = list(cmd1)
  fullpath1 = shutil.which(cmd1[0])
  if fullpath1 is None:
    raise SetuppyError(f"Could not find command: {cmd1[0]}")
  cmd1[0] = fullpath1

  cmd2 = list(cmd2)
  fullpath2 = shutil.which(cmd2[0])
  if fullpath2 is None:
    raise SetuppyError(f"Could not find command: {cmd2[0]}")
  cmd2[0] = fullpath2

  logging.info('Running command "%s | %s"', " ".join(cmd1), " ".join(cmd2))

  proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
  proc2 = subprocess.Popen(
    cmd2, stdin=proc1.stdout, stdout=subprocess.PIPE, encoding="utf-8"
  )
  stdout, stderr = proc2.communicate()
  return proc2.returncode, stdout, stderr
