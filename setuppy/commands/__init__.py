"""Registry for commands."""

from typing import Type

from setuppy.commands import apt
from setuppy.commands import brew
from setuppy.commands import github
from setuppy.commands import stow
from setuppy.commands.command import Command


CommandRegistry: dict[str, Type[Command]] = dict()


def register(cls: Type[Command]) -> Type[Command]:
  """Register the command type."""
  CommandRegistry[cls.__name__.lower()] = cls
  return cls


register(apt.Apt)
register(brew.Brew)
register(github.Github)
register(stow.Stow)
