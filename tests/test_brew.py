"""Test for the brew command."""

from collections.abc import Iterable
from unittest import mock

import pytest

from setuppy.commands.brew import Brew
from setuppy.types import SetuppyError


PACKAGES = ["foo", "bar", "baz"]
CMD_QUERY_FORMULA = ["brew", "list", "--formula", "-1"]
CMD_QUERY_CASK = ["brew", "list", "--cask", "-1"]
CMD_INSTALL = ["brew", "install"]


@pytest.fixture
def run_command() -> Iterable[mock.MagicMock]:
  patcher = mock.patch("setuppy.commands.brew.run_command")
  run_command = patcher.start()
  run_command.return_value = (0, "", "")
  yield run_command
  patcher.stop()


def test_list_fails(run_command: mock.MagicMock):
  # Run brew list and raise an exception if there's an error.
  run_command.return_value = (1, "", "")
  brew = Brew(PACKAGES)
  with pytest.raises(SetuppyError):
    brew(facts={}, simulate=False)
  assert run_command.call_count == 1
  run_command.assert_any_call(CMD_QUERY_FORMULA)

  # Same as above but fail on the brew list --casks call.
  run_command.reset_mock()
  run_command.side_effect = [(0, "", ""), (1, "", "")]
  brew = Brew(PACKAGES)
  with pytest.raises(SetuppyError):
    brew(facts={}, simulate=False)
  assert run_command.call_count == 2
  run_command.assert_any_call(CMD_QUERY_FORMULA)
  run_command.assert_any_call(CMD_QUERY_CASK)


def test_all_installed(run_command: mock.MagicMock):
  # If all the packages are installed then we should set rv.changed=False and
  # should skip the brew install command.
  run_command.return_value = (0, "\n".join(PACKAGES), "")
  brew = Brew(PACKAGES)
  rv = brew(facts={}, simulate=False)
  assert not rv.changed
  assert run_command.call_count == 2
  run_command.assert_any_call(CMD_QUERY_FORMULA)
  run_command.assert_any_call(CMD_QUERY_CASK)


def test_all_installed_cached(run_command: mock.MagicMock):
  # Same as above but we'll get the information from the cache and shouldn't
  # call run_command at all.
  brew = Brew(PACKAGES)
  rv = brew(facts={"brew_packages": PACKAGES}, simulate=False)
  assert not rv.changed
  assert not run_command.called


def test_install(run_command: mock.MagicMock):
  # Use the cache so we skip querying installed packages. We leave one package
  # out so we should try and install it.
  brew = Brew(PACKAGES)
  rv = brew(facts={"brew_packages": PACKAGES[:-1]}, simulate=False)
  assert rv.changed
  run_command.assert_called_once_with([*CMD_INSTALL, PACKAGES[-1]])


def test_install_error(run_command: mock.MagicMock):
  # Same as above but the installation command errors so we should raise an
  # exception.
  run_command.return_value = (1, "", "")
  brew = Brew(PACKAGES)
  with pytest.raises(SetuppyError):
    brew(facts={"brew_packages": PACKAGES[:-1]}, simulate=False)
  run_command.assert_called_once_with([*CMD_INSTALL, PACKAGES[-1]])


def test_install_simulate(run_command: mock.MagicMock):
  # Same as above but simulate, so we shouldn't run the command.
  brew = Brew(PACKAGES)
  rv = brew(facts={"brew_packages": PACKAGES[:-1]}, simulate=True)
  assert rv.changed
  assert not run_command.called
