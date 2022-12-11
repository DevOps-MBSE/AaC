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

    def to_tuple(self) -> tuple[int, int, int, int]:
        """
        Return a representation of the location as a tuple.

        Returns:
            An (int, int, int, int) tuple consisting of the line number, column, character start, and the span.
        """
        return self.line, self.column, self.position, self.span
