"""Test for the raw "command" command."""

from unittest.mock import patch

import pytest

from setuppy.commands.apt import Apt
from setuppy.types import SetuppyError


@patch("setuppy.commands.apt.run_command")
def test_command(rc):
  apt = Apt(["foo", "bar", "baz"])

  # Run dpkg and raise an error if that fails.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    apt(facts={}, simulate=True)

  # Run dpkg to find installed packages for which we'll return all of them. The
  # command should return not changed and we should only run the dpkg command.
  rc.reset_mock()
  rc.return_value = (0, "foo\nbar\nbaz", "")
  rv = apt(facts={}, simulate=False)
  assert not rv.changed
  rc.assert_called_once_with(r"dpkg-query -f '${binary:Package}\n' -W")

  # Skip dpkg because we have "cached" apt_packages; the baz package is missing
  # so this results in a change, but we don't call the apt command because
  # simulate is True.
  rc.reset_mock()
  rc.return_value = (0, "", "")
  rv = apt(facts={"apt_packages": ["foo", "bar"]}, simulate=True)
  assert rv.changed
  assert not rc.called

  # Skip dpkg because we have "cached" apt_packages; try to install baz, but
  # raise an error if the apt-get command fails.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    apt(facts={"apt_packages": ["foo", "bar"]}, simulate=False)

  # Skip dpkg because we have "cached" apt_packages; try to install baz and make
  # sure we properly call apt-get.
  rc.reset_mock()
  rc.return_value = (0, "", "")
  rv = apt(facts={"apt_packages": ["foo", "bar"]}, simulate=False)
  assert rv.changed
  rc.assert_called_once_with("apt-get -y install baz", sudo=True)
