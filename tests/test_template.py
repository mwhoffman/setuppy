"""Test for the template command."""

import pathlib

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from setuppy.commands.template import Template
from setuppy.types import SetuppyError


SOURCE = "/source"
DEST = "/dest"


def test_exists_is_file(fs: FakeFilesystem):
  # Raise an error if SOURCE exists, but is a file.
  fs.create_file(SOURCE)
  template = Template(SOURCE, DEST)
  with pytest.raises(SetuppyError):
    template(facts={}, simulate=False)


def test_source_empty(fs: FakeFilesystem):
  # No changes should occur if the SOURCE directory is empty.
  fs.create_dir(SOURCE)
  template = Template(SOURCE, DEST)
  rv = template(facts={}, simulate=False)
  assert not rv.changed
  # We didn't create the destination directory so nothing should exist. But
  # we'll check both just to be pedantic.
  assert not pathlib.Path(DEST).exists()
  assert list(pathlib.Path(DEST).glob("*")) == []


def test_target_exists_is_file(fs: FakeFilesystem):
  # Raise an error if an existing target is a directory not a file.
  fs.create_file(SOURCE + "/foo", contents="foo")
  fs.create_dir(DEST + "/foo")
  template = Template(SOURCE, DEST)
  with pytest.raises(SetuppyError):
    template(facts={}, simulate=False)


def test_target_exists(fs: FakeFilesystem):
  # No changes should occur if the target already exists.
  fs.create_file(SOURCE + "/foo", contents="foo")
  fs.create_file(DEST + "/foo", contents="bar")
  template = Template(SOURCE, DEST)
  rv = template(facts={}, simulate=False)
  assert not rv.changed
  assert pathlib.Path(DEST + "/foo").read_text() == "bar"


def test_template(fs: FakeFilesystem):
  # Make sure we create the file, do the templating using format, and that we
  # can create intermediate directories.
  fs.create_file(SOURCE + "/foo/bar/baz", contents="{foo}")
  fs.create_dir(DEST + "/foo/bar")
  template = Template(SOURCE, DEST)
  rv = template(facts={"foo": "bar"}, simulate=False)
  assert rv.changed
  assert pathlib.Path(DEST + "/foo/bar/baz").read_text() == "bar"


def test_simulate(fs: FakeFilesystem):
  # Same as above, but simulate so the file shouldn't exist.
  fs.reset()
  fs.create_file(SOURCE + "/foo/bar", contents="{foo}")
  template = Template(SOURCE, DEST)
  rv = template(facts={"foo": "bar"}, simulate=True)
  assert rv.changed
  assert not pathlib.Path(DEST + "/foo/bar").exists()
