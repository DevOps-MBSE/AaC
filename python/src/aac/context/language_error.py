from attr import attrib, attrs, validators

@attrs(slots=True)
class LanguageError(Exception):
    """A base class representing a language error condition."""

    message: str = attrib(validator=validators.instance_of(str))