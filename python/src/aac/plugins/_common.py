"""Common utilities usable by all the plugins."""
from aac.io.parser import parse
from aac.io.parser._parser_error import ParserError
from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path


def get_plugin_definitions_from_yaml(package, filename) -> list[Definition]:
    """Return the parsed plugin definitions from the plugin definition file."""
    try:
        yaml_definitions = parse(get_resource_file_contents(package, filename), get_resource_file_path(package, filename))
    except ParserError as error:
        raise ParserError(error.source, error.errors) from None
    else:
        return yaml_definitions
