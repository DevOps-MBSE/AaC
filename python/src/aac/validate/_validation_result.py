from enum import Enum, auto
from typing import Callable

from attr import attrib, attrs, validators, Factory


class Severity(Enum):
    """A message severity for distinguishing between different kinds of ValidationResult messages."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of the validation of a single definition.

    Attributes:
        definitions (list): Definitions that were part of the validated content
        messages (dict[Severity, list]): A dictionary of messages of different severities.
        is_valid (Callable): A function that accepts a ValidationResult and returns True if it
                             should be considered valid or False if it should be considered invalid.
    """

    def _is_valid(self):
        """
        Return True if there are no error messages on the validation result; False, otherwise.

        This is a default implementation for determining if a ValidationResult is valid, or not.
        """
        return len(self.messages.get(Severity.ERROR, [])) == 0

    definitions: list = attrib(validator=validators.instance_of(list))
    messages: dict[Severity, list[str]] = attrib(default=Factory(dict), validator=validators.instance_of(dict))
    is_valid: Callable = attrib(default=_is_valid, validator=validators.is_callable())
