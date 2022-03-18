""""""

from attr import attrib, attrs, validators

from aac.parser.SourceLocation import SourceLocation


@attrs
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
