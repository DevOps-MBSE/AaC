"""Module contain common functionality shared by the various LSP providers."""
import logging


def get_symbol_at_position(content: str, offset: int) -> str:
    """
    Return the word at or adjacent to the offset location.

    Args:
        content (str): A container mapping document names to the associated LSP document.
        offset (int): The URI of the file that's currently active.
        position (Position): The position of the cursor in `current_uri` whose definition is being searched.

    Returns:
        A list of Locations at which the item at `position` is defined. If there is nothing
        found at the specified position, an empty list is returned.
    """
    at_end_of_file = offset >= len(content) - 1
    at_beginning_of_file = offset == 0
    on_symbol = not content[:offset].isspace()

    is_offset_preceded_by_a_space = (offset > 0 and content[offset - 1] == " ")
    at_beginning_of_symbol = (at_beginning_of_file or is_offset_preceded_by_a_space) and not at_end_of_file

    is_offset_a_space = (offset < len(content) and content[offset] == " ")
    at_end_of_symbol = (at_end_of_file or is_offset_a_space) and not at_beginning_of_file

    symbol = ""
    if on_symbol:
        symbol_start = 0
        symbol_end = len(content) - 1
        try:
            symbol_start = content.rindex(" ", 0, offset)
            symbol_end = content.index(" ", offset, len(content))
        except Exception as error:
            logging.info(f"Soft-error when attempting to locate symbol for LSP provider request: {error}")

        start_index = offset if at_beginning_of_symbol else symbol_start
        end_index = offset if at_end_of_symbol else symbol_end

        symbol = content[start_index:end_index].strip()

    return symbol
