"""Test for the curl command."""

from collections.abc import Iterable
from unittest import mock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands.curl import Curl
from setuppy.types import SetuppyError


URL = "http://foo.com/bar.tar.xz"
DEST = "/"
TARGET = "/bar"


@pytest.fixture
def run_pipe() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.curl.run_pipe")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


def test_invalid_suffix(
  run_pipe: mock.MagicMock,
):
  # A command with an invalid suffix should raise an exception.
  curl = Curl(sources=["http://foo.com/bar.tar.gz"], dest="/")
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
  assert not run_pipe.called


def test_exists(
  run_pipe: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Do nothing if the target directory exists.
  fs.create_dir(TARGET)
  curl = Curl([URL], dest=DEST)
  rv = curl(facts={}, simulate=False)
  assert not run_pipe.called
  assert not rv.changed


def test_exists_is_file(
  run_pipe: mock.MagicMock,
  fs: FakeFilesystem,
):
  # Raise an error if the target exists but is a file.
  fs.create_file("/bar")
  curl = Curl([URL], dest=DEST)
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
  assert not run_pipe.called


def test_command(
  run_pipe: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Make sure we run the command.
  curl = Curl([URL], dest=DEST)
  rv = curl(facts={}, simulate=False)
  assert rv.changed
  cmd1 = ["curl", "-sSL", URL]
  cmd2 = ["tar", "-xJf", "-", "-C", TARGET]
  run_pipe.assert_called_once_with(cmd1, cmd2)


def test_simulate(
  run_pipe: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Same as above but we'll simulate so the command shouldn't be called.
  curl = Curl([URL], dest=DEST)
  rv = curl(facts={}, simulate=True)
  assert rv.changed
  assert not run_pipe.called


def test_command_fails(
  run_pipe: mock.MagicMock,
  fs: FakeFilesystem,  # noqa: ARG001
):
  # Same as above but raise an exception if the command fails.
  run_pipe.return_value = (1, "", "")
  curl = Curl([URL], dest=DEST)
  with pytest.raises(SetuppyError):
    curl(facts={}, simulate=False)
