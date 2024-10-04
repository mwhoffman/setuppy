"""Logger."""

class Logger:
  """Logger class."""

  def __init__(self, verbosity: int, indent: int=0):
    """Initialize the logger."""
    self._verbosity = verbosity
    self._indent = indent

  def log(self, text: str, level: int=0):
    """Log output."""
    if self._verbosity >= level:
      print(" " * (self._indent * 2) + text)

  def indent(self) -> "Logger":
    """Return a Logger with increased indent."""
    return Logger(self._verbosity, self._indent+1)
