"""Provides lexical unit for a parsed AaC definition."""

from attr import attrib, attrs, validators

from aac.io.paths import is_same_file
from aac.lang.definitions.source_location import SourceLocation


@attrs(eq=False)
class Lexeme:
    """A lexical unit for a parsed AaC definition.

    Attributes:
        location (SourceLocation): The location at which the object was found.
        source (str): The source in which the object was found.
        value (str): The value of the parsed object.
    """

    location: SourceLocation = attrib(validator=validators.instance_of(SourceLocation))
    source: str = attrib(validator=validators.instance_of(str))
    value: str = attrib(validator=validators.instance_of(str))

    def __eq__(self, __o) -> bool:
        """Return whether this Lexeme is the same as __o."""
        return (
            isinstance(__o, Lexeme)
            and self.value == __o.value
            and self.location == __o.location
            and is_same_file(self.source, __o.source)
        )
