"""Facts."""

import os
from typing import Any


type Facts = dict[str, Any]


def get_facts() -> Facts:
  """Get basic system facts."""
  facts = dict()
  facts["home"] = os.getenv("HOME")
  facts["user"] = os.getenv("USER")
  facts["cwd"] = os.getcwd()
  facts["uname"] = os.uname().sysname
  return facts


