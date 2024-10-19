"""Test for the template command."""

import pathlib

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands.template import Template
from setuppy.types import SetuppyError


def test_template(fs: FakeFilesystem):
  source = "/source"
  dest = "/dest"
  template = Template(source, dest)

  # Raise an error if source exists, but is a file.
  fs.reset()
  fs.create_file("/source")
  with pytest.raises(SetuppyError):
    template(facts={}, simulate=False)

  # No changes should occur if the source directory is empty.
  fs.reset()
  fs.create_dir(source)
  rv = template(facts={}, simulate=False)
  assert not rv.changed
  # We didn't create the destination directory so nothing should exist. But
  # we'll check both just to be pedantic.
  assert not pathlib.Path(dest).exists()
  assert list(pathlib.Path(dest).glob("*")) == []

  # Raise an error if an existing target is a directory not a file.
  fs.reset()
  fs.create_file(source + "/foo", contents="foo")
  fs.create_dir(dest + "/foo")
  with pytest.raises(SetuppyError):
    template(facts={}, simulate=False)

  # No changes should occur if the target already exists.
  fs.reset()
  fs.create_file(source + "/foo", contents="foo")
  fs.create_file(dest + "/foo", contents="bar")
  rv = template(facts={}, simulate=False)
  assert not rv.changed
  assert pathlib.Path(dest + "/foo").read_text() == "bar"

  # Make sure we create the file, do the templating using format, and that we
  # can create intermediate directories.
  fs.reset()
  fs.create_file(source + "/foo/bar", contents="{foo}")
  rv = template(facts={"foo": "bar"}, simulate=False)
  assert rv.changed
  assert pathlib.Path(dest + "/foo/bar").read_text() == "bar"

  # Same as above, but simulate so the file shouldn't exist.
  fs.reset()
  fs.create_file(source + "/foo/bar", contents="{foo}")
  rv = template(facts={"foo": "bar"}, simulate=True)
  assert rv.changed
  assert not pathlib.Path(dest + "/foo/bar").exists()
