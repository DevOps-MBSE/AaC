"""Functions to allow interacting with the core AaC spec."""
import copy

from aac.lang.constants import DEFINITION_FIELD_FIELDS, DEFINITION_NAME_ROOT, ROOT_KEY_SCHEMA
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.io.parser import parse
from aac.io.parser._parser_error import ParserError

PRIMITIVES: list[str] = []
ROOT_NAMES: list[str] = []
AAC_CORE_SPEC_DEFINITIONS: list[Definition] = []
CORE_SPEC_FILE_NAME = "spec.yaml"


def get_aac_spec() -> list[Definition]:
    """
    Get the specification for Architecture-as-Code itself.

    The AaC model specification is
    defined as an AaC model and is needed for model validation.

    Returns:
        Returns a list of parsed definitions that compose the core
        AaC specification.
    """

    def set_files_to_not_user_editable(definition):
        definition.source.is_user_editable = False

    global AAC_CORE_SPEC_DEFINITIONS
    if not len(AAC_CORE_SPEC_DEFINITIONS) > 0:
        core_spec_as_yaml = get_aac_spec_as_yaml()
        try:
            AAC_CORE_SPEC_DEFINITIONS = parse(core_spec_as_yaml, _get_aac_spec_file_path())
        except ParserError as error:
            raise ParserError(error.source, error.errors) from None
        else:
            list(map(set_files_to_not_user_editable, AAC_CORE_SPEC_DEFINITIONS))

    return AAC_CORE_SPEC_DEFINITIONS


def get_aac_spec_as_yaml() -> str:
    """Get the base AaC spec in YAML.

    Utility to provide the current base AaC model specification in an easy to read yaml format,
    just as it is defined internally.

    See get_aac_active_context_as_yaml() to get the core AaC spec and all extensions (including
    those added by all loaded plugins) as a YAML string.

    Returns:
        Returns a string containing YAML for the current AaC spec.  Each model entry is separated
        by the "---" yaml syntax representing separate files to be parsed.
    """
    return get_resource_file_contents(__package__, CORE_SPEC_FILE_NAME)


def get_primitives(reload: bool = False) -> list[str]:
    """Gets the list of primitives as defined in the AaC model specification.

    Args:
        reload: If True the cached primitive values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each primitive type in the AaC model specification.
    """

    global PRIMITIVES

    if len(PRIMITIVES) == 0 or reload:
        aac_definitions = get_aac_spec()
        primitives_definition = get_definition_by_name("Primitives", aac_definitions)
        PRIMITIVES = copy.deepcopy(search_definition(primitives_definition, ["enum", "values"]))

    return PRIMITIVES


def get_root_keys(reload: bool = False) -> list[str]:
    """Gets the list of root names as defined in the AaC DSL specification.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each root name in the AaC model specification.
    """

    global ROOT_NAMES

    if len(ROOT_NAMES) == 0 or reload:
        ROOT_NAMES = [definition.get_root() for definition in get_aac_spec() if definition.get_root()]

    return ROOT_NAMES


def get_root_definitions(reload: bool = False) -> list[Definition]:
    """Gets the list of the root definitions declared in the AaC DSL specification.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of definitions representing the root items of the AaC language definition.
    """

    return [definition for definition in get_aac_spec() if definition.get_root()]


def _get_aac_spec_file_path() -> str:
    """Get the path for the spec file in the AaC package on the filesystem."""
    return get_resource_file_path(__package__, CORE_SPEC_FILE_NAME)
