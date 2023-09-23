"""A module for defining a finding location."""
from attr import attrib, attrs, validators
from typeguard import check_type

from aac.io.files.aac_file import AaCFile
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


@attrs(init=False, slots=True)
class FindingLocation:
    """
    A representation of the location of a validator finding.

    Attributes:
        validation_name (str): The name of the validator plugin that made the finding.
        source_uri (AaCFile): The file in which the finding occurred.
        location (SourceLocation): The source location of the finding.
    """

    validation_name: str = attrib(validator=validators.instance_of(str))
    source: AaCFile = attrib(validator=validators.instance_of(AaCFile))
    location: SourceLocation = attrib(validator=validators.instance_of(SourceLocation))

    def __init__(self, validation_name: str, source_uri: AaCFile, line: int, column: int, position: int, span: int) -> None:
        """Initialize a new FindingLocation object."""
        self.validation_name = validation_name
        self.source = source_uri
        self.location = SourceLocation(line, column, position, span)

    def to_tuple(self) -> tuple[int, int, int, int]:
        """
        Return a representation of the location as a tuple.

        Returns:
            An (int, int, int, int) tuple consisting of the line number, column, character start, and the span.
        """
        return self.location.to_tuple()

    @staticmethod
    def from_lexeme(validation_name: str, lexeme: Lexeme) -> "FindingLocation":
        """
        Convert a lexeme to a FindingLocation.

        Args:
            validation_name (str): The validation's name. Used to report which validation found the finding.
            lexeme (Lexeme): The lexeme used to populate the finding's line, position, and span

        Returns:
            A FindingLocation set to the same location and span as the lexeme.
        """
        check_type("lexeme", lexeme, Lexeme)

        source_file = get_active_context().get_file_in_context_by_uri(lexeme.source) or AaCFile(lexeme.source, True, False)
        lexeme_location = lexeme.location
        return FindingLocation(
            validation_name,
            source_file,
            lexeme_location.line,
            lexeme_location.column,
            lexeme_location.position,
            lexeme_location.span,
        )
