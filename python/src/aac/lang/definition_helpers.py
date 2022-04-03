"""Arch-as-Code helper functions to simplify managing and working with parsed definitions/models."""

import logging
from typing import Optional

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.arrays import remove_list_type_indicator
from aac.lang.definitions.search import search_definition


def get_models_by_type(models: dict[str, dict], root_name: str) -> dict[str, dict]:
    """Gets subset of models of a specific root name.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed models to be "filtered" to a specific root name.

    Args:
        models (dict[str, dict]): The dict of models to search.
        root_name (str): The root name to filter on.

    Returns:
        A dict mapping type names to AaC model definitions.
    """
    ret_val = {}
    for key, value in models.items():
        if root_name in value.keys():
            ret_val[key] = value

    return ret_val


def get_definitions_by_root_key(root_key: str, definitions: list[Definition]) -> list[Definition]:
    """Return a subset of definitions with the given root key.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed definitions to be "filtered" to a specific root name.

    Args:
        root_key (str): The root key to filter on.
        definitions (list[Definition]): The list of parsed definitions to search.

    Returns:
        A list of ParedDefinitions with the given root key AaC model definitions.
    """

    def does_definition_root_match(definition: Definition) -> bool:
        return root_key == definition.get_root_key()

    return list(filter(does_definition_root_match, definitions))


def get_definition_by_name(definition_name: str, definitions: list[Definition]) -> Optional[Definition]:
    """Return a definition with a matching name from a list of definitions.

    Args:
        definition_name (str): The definition's name to locate.
        definitions (list[Definition]): The list of definitions to search through

    Returns:
        A Definition with the given name or None.
    """

    def does_definition_name_match(parsed_definition: Definition) -> bool:
        return remove_list_type_indicator(definition_name) == parsed_definition.name

    matching_definitions = list(filter(does_definition_name_match, definitions))
    matching_definitions_count = len(matching_definitions)

    result = None
    if matching_definitions_count > 1:
        multiple_definitions_found_error = f"Found multiple definitions with the same name '{definition_name}'\n{matching_definitions}'"
        logging.error(multiple_definitions_found_error)
        raise RuntimeError(f'Found multiple definitions with the same name "{definition_name}"\n{matching_definitions}')

    elif matching_definitions_count < 1:
        logging.debug(f'Failed to find a definition with the name "{definition_name}"')

    else:
        result = matching_definitions[0]

    return result


def convert_parsed_definitions_to_dict_definition(definitions: list[Definition]) -> dict:
    """
    DEPRECATED: Returns a combined dict from the list of Definitions.

    This function is intended only as a stop-gap to support some implementations until they have been fully
    converted to utilize the Definition class instead of python dictionaries.

    """
    return {definition.name: definition.structure for definition in definitions}


def get_definition_fields_and_types(
    parsed_definition: Definition, context_definitions: list[Definition]
) -> dict[str, Definition]:
    """Return a list of field names to their definition types."""
    root_definition = get_definition_by_name("root", context_definitions)
    root_fields = search_definition(root_definition, ["data", "fields"])
    roots_dict = {field.get("name"): field.get("type") for field in root_fields}
    root_definition_name = roots_dict.get(parsed_definition.get_root_key())

    definition_structure = get_definition_by_name(root_definition_name, context_definitions)
    defined_fields = search_definition(definition_structure, [definition_structure.get_root_key(), "fields"])

    field_types = {}
    for field in defined_fields:
        field_name = field.get("name")
        field_type = field.get("type")

        type_definition = get_definition_by_name(field_type, context_definitions) or field_type
        field_types = field_types | {field_name: type_definition}

    return field_types
