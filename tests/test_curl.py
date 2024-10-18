"""Test for the curl command."""

from unittest.mock import patch

import pytest

from setuppy.commands.curl import Curl
from setuppy.types import SetuppyError


@patch("setuppy.commands.curl.run_pipe")
def test_curl(rp, fs):
  url = "http://foo.com/bar.tar.xz"
  dest = "/"
  curl = Curl([url], dest)

  # rv.changed should be True if the file doesn't exist.
  rv = curl(facts={}, simulate=True)
  assert rv.changed
  assert not rp.called

  # Do nothing if the target dir already exists.
  fs.create_dir("/bar")
  rv = curl(facts={}, simulate=True)
  assert not rv.changed
  assert not rp.called

  # Raise an error if the target exists and is a file.
  fs.reset()
  fs.create_file("/bar")
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=True)

  # Make sure we run the command.
  fs.reset()
  rp.return_value = (0, "", "")
  rv = curl(facts={}, simulate=False)
  assert rv.changed
  rp.assert_called_once_with(f"curl -sSL {url}", "tar -xJf - -C /bar")

  # Raise an error if the command fails.
  fs.reset()
  rp.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)

  # Raise an error if we don't know how to handle the suffix.
  url = "http://foo.com/bar.tar.gz"
  dest = "/"
  curl = Curl([url], dest)
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=True)
