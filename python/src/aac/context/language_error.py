"""An exception class representing a language error condition."""
from attr import attrib, attrs, validators
from typing import Optional


@attrs(slots=True)
class LanguageError(Exception):
    """A base class representing a language error condition."""
    message: str = attrib(validator=validators.instance_of(str))
    location: Optional[str] = attrib(validator=validators.optional(validators.instance_of(str)))
