"""Test for the github command."""

from unittest import mock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands.github import Github
from setuppy.types import SetuppyError


@mock.patch("setuppy.commands.github.run_command")
def test_github(rc: mock.MagicMock, fs: FakeFilesystem):
  repo = "mwhoffman/setuppy"
  dest = "/"
  github = Github([repo], dest)

  cmd_get_url = "git --git-dir=/setuppy/.git remote get-url origin"
  cmd_clone = f"git clone https://github.com/{repo} /setuppy"

  # Make the run_command function return success so that if we do call it we can
  # raise an assertion error rather than having it fail within the command call.
  rc.return_value = (0, "", "")

  # Raise an exception if target exists and is not a dir.
  rc.reset_mock()
  fs.reset()
  fs.create_file("/setuppy")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not rc.called

  # Raise an exception if target/.git doesn't exist.
  rc.reset_mock()
  fs.reset()
  fs.create_dir("/setuppy/")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not rc.called

  # Raise an exception if target/.git exists and is not a dir.
  rc.reset_mock()
  fs.reset()
  fs.create_file("/setuppy/.git")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  assert not rc.called

  # Raise an exception the get-url command fails.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  fs.reset()
  fs.create_dir("/setuppy/.git")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  rc.assert_called_once_with(cmd_get_url)

  # Raise an exception if the get-url command returns the wrong repo.
  rc.reset_mock()
  rc.return_value = (0, "https://foo.com", "")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  rc.assert_called_once_with(cmd_get_url)

  # Make sure we skip the command if the repo exists.
  rc.reset_mock()
  rc.return_value = (0, f"https://github.com/{repo}", "")
  rv = github(facts={}, simulate=False)
  assert not rv.changed
  rc.assert_called_once_with(cmd_get_url)

  # Make sure we run the command.
  fs.reset()
  rc.reset_mock()
  rc.return_value = (0, "", "")
  rv = github(facts={}, simulate=False)
  assert rv.changed
  rc.assert_called_once_with(cmd_clone)

  # Same as above, but don't call the command if we're simulating.
  rc.reset_mock()
  rv = github(facts={}, simulate=True)
  assert rv.changed
  assert not rc.called

  # Raise an exception if the command returns an error.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)
  rc.assert_called_once_with(cmd_clone)
