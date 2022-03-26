"""Functions to allow interacting with the core AaC spec."""

from aac.parser import parse, ParsedDefinition
from aac.package_resources import get_resource_file_contents
from aac.lang.definition_helpers import get_definitions_by_root_key, search, get_definition_by_name

PRIMITIVES: list[str] = []
ROOT_NAMES: list[str] = []
AAC_CORE_SPEC_DEFINITIONS: list[ParsedDefinition] = []
CORE_SPEC_FILE_NAME = "spec.yaml"


def get_aac_spec() -> list[ParsedDefinition]:
    """
    Get the specification for Architecture-as-Code itself.

    The AaC model specification is
    defined as an AaC model and is needed for model validation.

    Returns:
        Returns a list of parsed definitions that compose the core
        AaC specification.
    """
    global AAC_CORE_SPEC_DEFINITIONS
    if len(AAC_CORE_SPEC_DEFINITIONS) > 0:
        # already parsed, just return cached values
        aac_data = get_definitions_by_root_key(AAC_CORE_SPEC_DEFINITIONS, "data")
        aac_enums = get_definitions_by_root_key(AAC_CORE_SPEC_DEFINITIONS, "enum")
        return aac_data + aac_enums

    core_spec_as_yaml = get_aac_spec_as_yaml()
    AAC_CORE_SPEC_DEFINITIONS = parse(core_spec_as_yaml)
    aac_data = get_definitions_by_root_key(AAC_CORE_SPEC_DEFINITIONS, "data")
    aac_enums = get_definitions_by_root_key(AAC_CORE_SPEC_DEFINITIONS, "enum")

    return aac_data + aac_enums


def get_aac_spec_as_yaml() -> str:
    """Get the base AaC spec in YAML.

    Utility to provide the current base AaC model specification (including plugin extensions)
    in an easy to read yaml format (just as it is defined internally).

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
        primitives_definition = get_definition_by_name(aac_definitions, "Primitives")
        PRIMITIVES = search(primitives_definition.definition, ["enum", "values"])

    return PRIMITIVES


def get_root_keys(reload: bool = False) -> list[str]:
    """Gets the list of root names as defined in the AaC DSL specification.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each root name in the AaC model specification.
    """

    def get_field_name(fields_entry_dict: dict):
        return fields_entry_dict.get("name")

    global ROOT_NAMES

    if len(ROOT_NAMES) == 0 or reload:
        aac_definitions = get_aac_spec()
        root_definition = get_definition_by_name(aac_definitions, "root")
        ROOT_NAMES = list(map(get_field_name, search(root_definition.definition, ["data", "fields"])))

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
    root_definition = get_definition_by_name(aac_definitions, "root")

    return search(root_definition.definition, ["data", "fields"])
