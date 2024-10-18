"""Test for the raw "command" command."""

from unittest.mock import patch

import pytest

from setuppy.commands.apt import Apt
from setuppy.types import SetuppyError


def test_command():
  apt = Apt(["foo", "bar", "baz"])

  # Call dpkg, but mark no changes since everything is installed. Skip the
  # command due to the simulate flag.
  with patch("setuppy.commands.apt.run_command") as rc:
    rc.return_value = (0, "foo\nbar\nbaz", "")
    rv = apt(facts={}, simulate=True)
    dpkg = r"dpkg-query -f '${binary:Package}\n' -W"
    assert not rv.changed
    rc.assert_called_once_with(dpkg)

  # Skip dpkg, because we've cached installed packages. Also skip running the
  # command because of the simulate flag. Mark a change because we're missing
  # the "baz" package.
  with patch("setuppy.commands.apt.run_command") as rc:
    rc.return_value = (0, "", "")
    rv = apt(facts={"apt_packages": ["foo", "bar"]}, simulate=True)
    dpkg = r"dpkg-query -f '${binary:Package}\n' -W"
    assert rv.changed
    assert not rc.called

  # Raise an error if the command fails.
  with patch("setuppy.commands.apt.run_command") as rc:
    rc.return_value = (1, "", "")
    with pytest.raises(SetuppyError):
      apt(facts={}, simulate=True)

  # Run the command and mark a change.
  with patch("setuppy.commands.apt.run_command") as rc:
    rc.return_value = (0, "", "")
    rv = apt(facts={"apt_packages": ["foo", "bar"]}, simulate=False)
    assert rv.changed
    rc.assert_called_once_with("apt-get -y install baz", sudo=True)

  # Run the command and raise an error if the command fails.
  with patch("setuppy.commands.apt.run_command") as rc:
    rc.return_value = (1, "", "")
    with pytest.raises(SetuppyError):
      apt(facts={"apt_packages": ["foo", "bar"]}, simulate=False)
