"""Test for the github command."""

import textwrap
from collections.abc import Iterable
from unittest import mock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands import stow as stow_lib
from setuppy.types import SetuppyError


@pytest.fixture
def run_command() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.stow.run_command")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


@mock.patch("setuppy.commands.stow._get_stow_version")
def test_stow(
  get_stow_version: mock.MagicMock,
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # We'll test the version code elsewhere, so just mock it here.
  get_stow_version.return_value = "2.3.1"

  # Create the command to test.
  package = "foo"
  stowdir = "/stow"
  targetdir = "/home"
  stow = stow_lib.Stow(package, stowdir, targetdir)

  # Raise an exception if the stowdir doesn't exist.
  with pytest.raises(SetuppyError):
    stow(facts={"stow_version": "2.3.1"}, simulate=False)

  # Raise an exception if the package dir doesn't exist.
  fs.create_dir(stowdir)
  with pytest.raises(SetuppyError):
    stow(facts={}, simulate=False)

  # Create the package dir.
  fs.create_dir(stowdir + "/" + package)

  # Call the command.
  run_command.reset_mock()
  rv = stow(facts={}, simulate=False)
  assert not rv.changed
  cmd = f"stow -v --no-folding -d {stowdir} -t {targetdir} -R {package}"
  run_command.assert_called_once_with(cmd.split())

  # Call the simulate command.
  run_command.reset_mock()
  rv = stow(facts={}, simulate=True)
  assert not rv.changed
  run_command.assert_called_once_with((cmd + " -n").split())

  stderr = textwrap.dedent("""
  UNLINK: foo
  LINK: bar => /stow/foo/bar
  """).strip()

  # Return a changed value if CONFLICTS match anything.
  run_command.reset_mock()
  run_command.return_value = (0, "", stderr)
  rv = stow(facts={}, simulate=False)
  assert rv.changed

  # Raise an exception if there was an error with the command. Note that here
  # there aren't any matching conflicts. We'll check that in another test.
  run_command.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    stow(facts={}, simulate=False)


def test_version(
  run_command: mock.MagicMock,
):
  # Raise an exception if stow --version returns an error.
  run_command.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    stow_lib._get_stow_version()
  run_command.assert_called_once_with(["stow", "--version"])

  # Raise an exception if the version string isn't parseable.
  run_command.reset_mock()
  run_command.return_value = (0, "foo bar baz", "")
  with pytest.raises(SetuppyError):
    stow_lib._get_stow_version()

  # Raise an exception if the version is unsupported.
  run_command.reset_mock()
  run_command.return_value = (0, "stow (GNU Stow) version 1.1.1", "")
  with pytest.raises(SetuppyError):
    stow_lib._get_stow_version()

  # Raise an exception if the version is unsupported.
  run_command.reset_mock()
  run_command.return_value = (0, "stow (GNU Stow) version 2.3.1", "")
  version = stow_lib._get_stow_version()
  assert version == "2.3.1"


def test_conflicts():
  stderr = """
  * existing target is neither a link nor a directory: foo
  * existing target is neither a link nor a directory: bar
  """.strip()
  conflicts = stow_lib._get_conflicts_from_stderr(stderr, "2.3.1")
  assert conflicts == {"foo", "bar"}

  stderr = """
  * cannot stow /stow/foo/foo over existing target foo since neither a link nor a directory and --adopt not specified
  * cannot stow /stow/foo/bar over existing target bar since neither a link nor a directory and --adopt not specified
  """.strip()  # noqa: E501
  conflicts = stow_lib._get_conflicts_from_stderr(stderr, "2.4.0")
  assert conflicts == {"foo", "bar"}
