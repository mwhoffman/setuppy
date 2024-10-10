"""Utility functions for running commands."""

import logging
import shlex
import shutil
import subprocess

from setuppy.types import SetuppyError


def run_command(
  cmd: str,
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
  args = shlex.split(cmd)
  path = shutil.which(args[0])

  if path is None:
    raise SetuppyError(f"Could not find command: {args[0]}")

  args[0] = path

  if sudo:
    args = ["/usr/bin/sudo", *args]

  logging.info('Running command "%s"', " ".join(args))
  proc = subprocess.run(
    args, capture_output=True, encoding="utf-8", check=False
  )
  return proc.returncode, proc.stdout, proc.stderr


def run_pipe(cmd1: str, cmd2: str) -> tuple[int, str, str]:
  """Run the given command.

  Args:
    cmd1: the command and its arguments to run.
    cmd2: optional command to pipe the first into.

  Returns:
    A tuple (rc, stdout, stderr) containing the return code of the command and
    stdout and stderr as strings.
  """
  args1 = shlex.split(cmd1)
  path1 = shutil.which(args1[0])
  if path1 is None:
    raise SetuppyError(f"Could not find command: {args1[0]}")
  args1[0] = path1

  args2 = shlex.split(cmd2)
  path2 = shutil.which(args2[0])
  if path2 is None:
    raise SetuppyError(f"Could not find command: {args2[0]}")
  args2[0] = path2

  logging.info('Running command "%s | %s"', " ".join(args1), " ".join(args2))

  proc1 = subprocess.Popen(args1, stdout=subprocess.PIPE)
  proc2 = subprocess.Popen(
    args2, stdin=proc1.stdout, stdout=subprocess.PIPE, encoding="utf-8"
  )
  stdout, stderr = proc2.communicate()
  return proc2.returncode, stdout, stderr
