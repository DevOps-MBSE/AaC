"""Functions to allow interacting with the core AaC spec."""

from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.package_resources import get_resource_file_contents
from aac.parser import parse

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
    global AAC_CORE_SPEC_DEFINITIONS
    if not len(AAC_CORE_SPEC_DEFINITIONS) > 0:
        core_spec_as_yaml = get_aac_spec_as_yaml()
        AAC_CORE_SPEC_DEFINITIONS = parse(core_spec_as_yaml)

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
        PRIMITIVES = search_definition(primitives_definition, ["enum", "values"])

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
        ROOT_NAMES = [field.get("name") for field in get_root_fields()]

    return ROOT_NAMES


def get_root_fields(reload: bool = False) -> list[dict]:
    """Gets the list of the root fields declared in the AaC DSL specification.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of dictionaries representing the root keys and their contextual information.
    """

    aac_definitions = get_aac_spec()
    root_definition = get_definition_by_name("root", aac_definitions)

    return search_definition(root_definition, ["schema", "fields"])
