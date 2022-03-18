"""AaC Parser and related functions submodule."""

from aac.parser import parse_source
from aac.parser.ParsedDefinition import ParsedDefinition


def parse(source: str) -> list[ParsedDefinition]:
    """Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

    Args:
        source (str): Must be either a file path to an AaC yaml file or a string containing AaC definitions.

    Returns:
        A ParsedDefinition object containing the internal representation of the definition and metadata
        associated with the definition.
    """
    return parse_source.parse(source)


def get_yaml_from_source(source: str) -> str:
    """Get the YAML contents from the provided source.

    Args:
        source (str): The source from which to get the YAML contents. This can be a path-like
        string pointing to a file with YAML contents; or a string of YAML contents.

    Returns:
        The YAML contents extracted from source.
    """
    return parse_source.get_yaml_from_source(source)

