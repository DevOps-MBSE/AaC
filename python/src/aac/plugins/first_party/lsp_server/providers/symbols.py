"""Module contain common functionality shared by the various LSP providers."""
from enum import Enum
from typing import Optional
from pygls.lsp.types import Range, Position

from aac.lang.language_context import LanguageContext


class SymbolType(Enum):
    """Enums classifying the symbol type. Leveraged by providers to tailor responses."""

    DEFINITION_NAME = 1
    ENUM_VALUE_TYPE = 2
    ROOT_KEY_NAME = 3


def get_possible_symbol_types(name: str, language_context: LanguageContext) -> list[SymbolType]:
    """
    Return a list of enums indicating what kind of symbol this may be based on the language context.

    Args:
        name (str): The name or symbol to lookup
        language_context (LanguageContext): The language context to search for context for the symbol.

    Returns:
        A list of enums indicating a possible relationship between the name and content in the language context.
    """

    symbol_types = []

    if language_context.is_definition_type(name):
        symbol_types.append(SymbolType.DEFINITION_NAME)

    enum_definition = language_context.get_enum_definition_by_type(name)
    if enum_definition:
        symbol_types.append(SymbolType.ENUM_VALUE_TYPE)

    if name in language_context.get_root_keys():
        symbol_types.append(SymbolType.ROOT_KEY_NAME)

    return symbol_types


def get_symbol_at_position(content: str, line: int, column: int) -> Optional[str]:
    """
    Return the word at or adjacent to the offset location.

    Args:
        content (str): A container mapping document names to the associated LSP document.
        line (int): The line on which the cursor is positioned.
        column (int): The column on which the cursor is positioned.

    Returns:
        The symbol found at the current location in the content.
    """
    symbol_range = get_symbol_range_at_position(content, line, column)
    symbol = None
    if symbol_range:
        symbol_line = content.splitlines()[line]
        symbol = symbol_line[symbol_range.start.character:symbol_range.end.character]

    return symbol


def get_symbol_range_at_position(content: str, line: int, column: int) -> Optional[Range]:
    """Return the range of the symbol at the position."""
    content_lines = content.splitlines()
    line_with_symbol = content_lines[line]
    symbol_range = None

    if line_with_symbol != "":
        adjusted_column = column if column < len(line_with_symbol) else column - 1
        on_symbol = not line_with_symbol[adjusted_column].isspace()

        if on_symbol:

            symbol_start = 0
            # Reversed range from the adjusted column to the 0 element in the line
            for i in range(adjusted_column, -1, -1):
                if line_with_symbol[i].isspace():
                    break

                symbol_start = i

            symbol_end = len(line_with_symbol)
            for i in range(adjusted_column, len(line_with_symbol)):
                if line_with_symbol[i].isspace():
                    break

                symbol_end = i

            # Have to add 1 to the end index since slice ends are exclusive.
            symbol_end += 1

            start_position = Position(line=line, character=symbol_start)
            end_position = Position(line=line, character=symbol_end)
            symbol_range = Range(start=start_position, end=end_position)

    return symbol_range
