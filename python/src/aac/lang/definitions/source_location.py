"""Parser Metadata class use to manage and identify the location of definitions in the source YAML."""

from attr import attrib, attrs, validators


@attrs
class SourceLocation:
    """The position and span of an AaC structure in the YAML source.

    Attributes:
        line (int): The line number on which the object was found.
        column (int): The character position at which the object was found.
        position (int): The position relative to the start of the file where the object was found.
        span (int): The number of characters occupied by the object relative to `position`.
    """

    line: int = attrib(validator=validators.instance_of(int))
    column: int = attrib(validator=validators.instance_of(int))
    position: int = attrib(validator=validators.instance_of(int))
    span: int = attrib(validator=validators.instance_of(int))
