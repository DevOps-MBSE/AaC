"""AaC Parser and related functions submodule."""

from aac.parser._parse_source import parse
from aac.parser._parser_error import ParserError

__all__ = (
    ParserError.__name__,
    parse.__name__,
)
