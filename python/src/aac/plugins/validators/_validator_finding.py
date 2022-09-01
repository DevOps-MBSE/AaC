from enum import Enum, auto


class Severity(Enum):
    """A severity for distinguishing between different kinds of validator findings."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
