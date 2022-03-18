"""AaC Parser and related functions submodule."""

from aac.parser.parse import parse_source
from aac.parser.ParsedDefinition import ParsedDefinition


def parse(source: str) -> list[ParsedDefinition]:
    """Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

    Args:
        source (str): Must be either a file path to an AaC yaml file or a string containing AaC definitions.

    Returns:
        A ParsedDefinition object containing the internal representation of the definition and metadata
        associated with the definition.
    """
    return parse_source(source)
