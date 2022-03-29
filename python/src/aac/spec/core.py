"""Functions to allow interacting with the core AaC spec."""

import yaml

from typing import Iterable, Optional

from aac.parser import parse, ParsedDefinition
from aac.package_resources import get_resource_file_contents
from aac.util import get_models_by_type, search

PRIMITIVES: list[str] = []
ROOT_NAMES: list[str] = []
AAC_MODEL: Optional[ParsedDefinition] = None


def get_aac_spec() -> tuple[dict[str, dict], dict[str, dict]]:
    """
    Get the specification for Architecture-as-Code itself.

    The AaC model specification is
    defined as an AaC model and is needed for model validation.

    Returns:
        Returns a tuple (aac_data, aac_enums), where aac_data is a dict of the AaC model spec
        with root types of data and aac_enums is a dict of the AaC model spec with root types
        of enum.

    """
    global AAC_MODEL
    if AAC_MODEL:
        # already parsed, just return cached values
        aac_data = get_models_by_type(AAC_MODEL.definition, "data")
        aac_enums = get_models_by_type(AAC_MODEL.definition, "enum")
        return aac_data, aac_enums

    model_content = get_resource_file_contents(__package__, "spec.yaml")
    AAC_MODEL = parse(model_content)
    aac_data = get_models_by_type(AAC_MODEL.definition, "data")
    aac_enums = get_models_by_type(AAC_MODEL.definition, "enum")

    return aac_data, aac_enums


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
    aac_data, aac_enums = get_aac_spec()
    return format_as_yaml((aac_data | aac_enums).values())


def get_aac_active_context_as_yaml() -> str:
    """Get the active context in YAML.

    The active context is a superset of the core spec but also includes any definitions defined by
    loaded plugins, etc.

    See get_aac_spec_as_yaml() to get just the core AaC spec as a YAML string.

    Returns:
        Return a string containing YAML for the currently active context.
    """
    # TODO: Fill this in when we can.
    return f"Not implemented!\n{format_as_yaml({}.values())}"


# TODO: Move to definition_helpers module
def format_as_yaml(definitions: Iterable) -> str:
    """Format the definitions as a YAML string.

    Args:
        definitions (Iterable): The list of definitions to format as a YAML string.

    Returns:
        A YAML string containing the definitions.
    """
    return "---\n".join([yaml.dump(definition) for definition in definitions])


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
        _, aac_enums = get_aac_spec()
        PRIMITIVES = search(aac_enums["Primitives"], ["enum", "values"])

    return PRIMITIVES


def get_roots(reload: bool = False) -> list[str]:
    """Gets the list of root names as defined in the AaC model specification.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each root name in the AaC model specification.
    """

    global ROOT_NAMES

    if len(ROOT_NAMES) == 0 or reload:
        aac_data, _ = get_aac_spec()
        ROOT_NAMES = search(aac_data["root"], ["data", "fields", "name"])

    return ROOT_NAMES
