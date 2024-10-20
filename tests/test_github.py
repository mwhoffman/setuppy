"""Test for the github command."""

from collections.abc import Iterable
from unittest import mock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands.github import Github
from setuppy.types import SetuppyError


REPO = "bar"
SOURCE = f"foo/{REPO}"
TARGET = f"/{REPO}"
URL = f"https://github.com/{SOURCE}"
CMD_QUERY = ["git", "--git-dir", f"/{REPO}/.git", "remote", "get-url", "origin"]
CMD_CLONE = ["git", "clone", URL, TARGET]


@pytest.fixture
def run_command() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.github.run_command")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


def test_exists_not_dir(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an exception if TARGET exists and is not a dir.
  fs.create_file(TARGET)
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not run_command.called


def test_exists_no_git(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an exception if TARGET/.git doesn't exist.
  fs.create_dir(TARGET)
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not run_command.called


def test_exists_git_not_dir(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an exception if TARGET/.git exists and is not a dir.
  fs.create_file(f"{TARGET}/.git")
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not run_command.called


def test_exists_get_url_fails(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an exception the get-url command fails.
  fs.create_dir(f"{TARGET}/.git")
  run_command.return_value = (1, "", "")
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  run_command.assert_called_once_with(CMD_QUERY)


def test_exists_wrong_repo(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an exception if the get-url command returns the wrong repo.
  fs.create_dir(f"{TARGET}/.git")
  run_command.return_value = (0, "https://foo.com", "")
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  run_command.assert_called_once_with(CMD_QUERY)


def test_exists(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Make sure we skip the command if the repo exists.
  fs.create_dir(f"{TARGET}/.git")
  run_command.return_value = (0, f"https://github.com/{SOURCE}", "")
  github = Github(sources=[SOURCE], dest="/")
  rv = github(facts={}, simulate=False)
  assert not rv.changed
  run_command.assert_called_once_with(CMD_QUERY)


def test_command_runs(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Make sure we run the command.
  github = Github(sources=[SOURCE], dest="/")
  rv = github(facts={}, simulate=False)
  assert rv.changed
  run_command.assert_called_once_with(CMD_CLONE)


def test_command_simulate(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Same as above, but don't call the command if we're simulating.
  github = Github(sources=[SOURCE], dest="/")
  rv = github(facts={}, simulate=True)
  assert rv.changed
  assert not run_command.called


def test_command_fails(
  run_command: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Raise an exception if the command returns an error.
  run_command.return_value = (1, "", "")
  github = Github(sources=[SOURCE], dest="/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  run_command.assert_called_once_with(CMD_CLONE)
