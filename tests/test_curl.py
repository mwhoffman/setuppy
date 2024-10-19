"""Test for the curl command."""

from unittest.mock import patch

import pytest

from setuppy.commands.curl import Curl
from setuppy.types import SetuppyError


@patch("setuppy.commands.curl.run_pipe")
def test_curl(rp, fs):
  # Create a command with an invalid suffix.
  url = "http://foo.com/bar.tar.gz"
  dest = "/"
  curl = Curl([url], dest)

  # Make the run_pipe command return success so that if we do call it we can
  # raise an assertion error rather than having it fail within the command call.
  rp.return_value = (0, "", "")

  # Running the invalid command should raise an error.
  rp.reset_mock()
  fs.reset()
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
  assert not rp.called

  # Create a valid command.
  url = "http://foo.com/bar.tar.xz"
  dest = "/"
  curl = Curl([url], dest)

  # Do nothing if the target directory exists.
  rp.reset_mock()
  fs.reset()
  fs.create_dir("/bar")
  rv = curl(facts={}, simulate=False)
  assert not rp.called
  assert not rv.changed

  # Raise an error if the target exists but is a file.
  rp.reset_mock()
  fs.reset()
  fs.create_file("/bar")
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
  assert not rp.called

  # Make sure we run the command.
  rp.reset_mock()
  fs.reset()
  rv = curl(facts={}, simulate=False)
  assert rv.changed
  rp.assert_called_once_with(f"curl -sSL {url}", "tar -xJf - -C /bar")

  # Same as above but we'll simulate so the command shouldn't be called.
  rp.reset_mock()
  fs.reset()
  rv = curl(facts={}, simulate=True)
  assert rv.changed
  assert not rp.called

  # Same as above but raise an exception if the command fails.
  rp.reset_mock()
  rp.return_value = (1, "", "")
  fs.reset()
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
