"""Test for the apt command."""

from collections.abc import Iterable
from unittest import mock

import pytest

from setuppy.commands.apt import Apt
from setuppy.types import SetuppyError


PACKAGES = ["foo", "bar", "baz"]


@pytest.fixture
def run_command() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.apt.run_command")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


def test_dpkg_fails(run_command: mock.MagicMock):
  # Run dpkg and raise an error if that fails.
  run_command.return_value = (1, "", "")
  apt = Apt(PACKAGES)
  with pytest.raises(SetuppyError):
    apt(facts={}, simulate=False)
  run_command.assert_called_once_with(r"dpkg-query -f '${binary:Package}\n' -W")


def test_all_installed(run_command: mock.MagicMock):
  # Run dpkg to find installed packages for which we'll return all of them. The
  # command should return not changed and we should only run the dpkg command.
  run_command.return_value = (0, "\n".join(PACKAGES), "")
  apt = Apt(PACKAGES)
  rv = apt(facts={}, simulate=False)
  assert not rv.changed
  run_command.assert_called_once_with(r"dpkg-query -f '${binary:Package}\n' -W")


def test_all_installed_cached(run_command: mock.MagicMock):
  # Same as above but we'll get the information from the cache and shouldn't
  # call run_command at all.
  apt = Apt(PACKAGES)
  rv = apt(facts={"apt_packages": PACKAGES}, simulate=False)
  assert not rv.changed
  assert not run_command.called


def test_install(run_command: mock.MagicMock):
  # Use the cache so we skip querying installed packages. We leave one package
  # out so we should try and install it.
  apt = Apt(PACKAGES)
  rv = apt(facts={"apt_packages": PACKAGES[:-1]}, simulate=False)
  assert rv.changed
  cmd = f"apt-get -y install {PACKAGES[-1]}"
  run_command.assert_called_once_with(cmd, sudo=True)


def test_install_error(run_command: mock.MagicMock):
  # Same as above but the installation command errors so we should raise an
  # exception.
  run_command.return_value = (1, "", "")
  apt = Apt(PACKAGES)
  with pytest.raises(SetuppyError):
    apt(facts={"apt_packages": PACKAGES[:-1]}, simulate=False)
  cmd = f"apt-get -y install {PACKAGES[-1]}"
  run_command.assert_called_once_with(cmd, sudo=True)


def test_install_simulate(run_command: mock.MagicMock):
  # Same as above but simulate, so we shouldn't run the command.
  apt = Apt(PACKAGES)
  rv = apt(facts={"apt_packages": PACKAGES[:-1]}, simulate=True)
  assert rv.changed
  assert not run_command.called
