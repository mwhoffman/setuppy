"""Test for the github command."""

from unittest.mock import patch

import pytest

from setuppy.commands.github import Github
from setuppy.types import SetuppyError


@patch("setuppy.commands.github.run_command")
def test_github(rc, fs):
  repo = "mwhoffman/setuppy"
  dest = "/"
  github = Github([repo], dest)

  # rv.changed should be True, but we simulate so the command should not be not
  # be called.
  rv = github(facts={}, simulate=True)
  assert rv.changed
  assert not rc.called

  # rv.changed should be True and we should call the git command.
  rc.return_value = (0, "", "")
  rv = github(facts={}, simulate=False)
  assert rv.changed
  rc.assert_called_once_with(f"git clone https://github.com/{repo} /setuppy")

  # Raise an error if the git command fails.
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)

  # Raise an error if the target exists and is a file.
  fs.create_file("/setuppy")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)

  # Raise an error if target/.git exists and is a file.
  fs.reset()
  fs.create_dir("/setuppy")
  fs.create_file("/setuppy/.git")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)

  # Raise an error if target/.git exists, is a dir, and `... get-url origin`
  # returns an error code.
  fs.reset()
  fs.create_dir("/setuppy")
  fs.create_dir("/setuppy/.git")
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)

  # Raise an error if target/.git exists, is a dir, and `... get-url origin`
  # returns a different url.
  rc.return_value = (0, "https://foo.com", "")
  with pytest.raises(SetuppyError):
    github(facts={}, simulate=False)

  # Otherwise skip running clone if the repo already exists and properly targets
  # the correct url.
  rc.reset_mock()
  rc.return_value = (0, f"https://github.com/{repo}", "")
  rv = github(facts={}, simulate=False)
  assert not rv.changed
  rc.assert_called_once()
