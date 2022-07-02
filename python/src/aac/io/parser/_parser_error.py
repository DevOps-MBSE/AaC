"""Custom ParserError class that represents errors encountered during the parsing process."""
from attr import Factory, attrib, attrs, validators


@attrs
class ParserError(BaseException):
    """An error that represents a file that could not be parsed."""

    source: str = attrib(validator=validators.instance_of(str))
    errors: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
