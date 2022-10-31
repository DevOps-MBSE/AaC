"""Common LSP Provider functions for locations."""

from pygls.lsp.types.basic_structures import Location, Position, Range

from aac.lang.definitions.lexeme import Lexeme


def get_location_from_lexeme(lexeme: Lexeme) -> Location:
    """Return a pygls Location from an AaC lexeme."""
    start_position = Position(line=lexeme.location.line, character=lexeme.location.column)
    end_position = Position(line=lexeme.location.line, character=lexeme.location.column + lexeme.location.span)
    return Location(uri=lexeme.source, range=Range(start=start_position, end=end_position))
