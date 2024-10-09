"""Registry for commands."""

from typing import Type

from setuppy.commands import apt
from setuppy.commands import brew
from setuppy.commands import github
from setuppy.commands import stow
from setuppy.commands.base import BaseCommand


CommandRegistry: dict[str, Type[BaseCommand]] = dict()


def register(cls: Type[BaseCommand]) -> Type[BaseCommand]:
  """Register the command type."""
  CommandRegistry[cls.__name__.lower()] = cls
  return cls


register(apt.Apt)
register(brew.Brew)
register(github.Github)
register(stow.Stow)
