"""Helper tools for converting between AaC objects and Pygls objects."""

from pygls.lsp import Position, Range
from typeguard import check_type

from aac.lang.definitions.source_location import SourceLocation


def source_location_to_position(location: SourceLocation) -> Position:
    """Convert a source location to a position."""
    check_type("location", location, SourceLocation)
    return Position(line=location.line, character=location.column)


def source_location_to_range(location: SourceLocation) -> Range:
    """Convert a source location to a range."""
    check_type("location", location, SourceLocation)
    return Range(
        start=Position(line=location.line, character=location.column),
        end=Position(line=location.line, character=location.column + location.span),
    )


def source_locations_to_range(location1: SourceLocation, location2: SourceLocation) -> Range:
    """Convert two source locations to a range."""
    check_type("location1", location1, SourceLocation)
    check_type("location2", location2, SourceLocation)
    return Range(
        start=Position(line=location1.line, character=location1.column),
        end=Position(line=location2.line, character=location2.column),
    )
