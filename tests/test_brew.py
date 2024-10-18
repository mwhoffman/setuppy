"""Test for the raw "command" command."""

from unittest.mock import patch

import pytest

from setuppy.commands.brew import Brew
from setuppy.types import SetuppyError


@patch("setuppy.commands.brew.run_command")
def test_brew(rc):
  brew = Brew(["foo", "bar", "baz"])

  # Run brew list and raise an exception if there's an error.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    brew(facts={}, simulate=True)

  # Same as above but fail on the brew list --casks call.
  rc.reset_mock()
  rc.side_effect = [(0, "", ""), (1, "", "")]
  with pytest.raises(SetuppyError):
    brew(facts={}, simulate=True)

  # Run brew list to find installed packages for which we'll return all of them.
  # The command should return not changed and we should only brew list twice.
  # Technically we're mocking that the given packages are both formulae and
  # casks, but treating this as a set will ignore this.
  rc.reset_mock(side_effect=True)
  rc.return_value = (0, "foo\nbar\nbaz", "")
  rv = brew(facts={}, simulate=False)
  assert not rv.changed
  rc.assert_any_call(r"brew list --formula -1")
  rc.assert_any_call(r"brew list --cask -1")

  # Skip brew list because we have "cached" brew_packages; the baz package is
  # missing so this results in a change, but we don't call brew install because
  # simulate is True.
  rc.reset_mock()
  rc.return_value = (0, "", "")
  rv = brew(facts={"brew_packages": ["foo", "bar"]}, simulate=True)
  assert rv.changed
  assert not rc.called

  # Skip brew list because we have "cached" brew_packages; try to install baz,
  # but raise an error if the brew install command fails.
  rc.reset_mock()
  rc.return_value = (1, "", "")
  with pytest.raises(SetuppyError):
    brew(facts={"brew_packages": ["foo", "bar"]}, simulate=False)

  # Skip brew list because we have "cached" brew_packages; try to install baz
  # and make sure we properly call brew install.
  rc.reset_mock()
  rc.return_value = (0, "", "")
  rv = brew(facts={"brew_packages": ["foo", "bar"]}, simulate=False)
  assert rv.changed
  rc.assert_called_once_with("brew install baz")
