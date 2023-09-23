"""Arch-as-Code helper functions to simplify managing and working with parsed definitions/models."""

import logging
from typing import Optional

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.type import remove_list_type_indicator


def get_models_by_type(models: dict[str, dict], root_name: str) -> dict[str, dict]:
    """Gets subset of models of a specific root name.

    The aac.io.parser.parse() function returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or schema).  This utility
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

    The aac.io.parser.parse() function returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or schema).  This utility
    method allows a setup of parsed definitions to be "filtered" to a specific root key.

    Args:
        root_key (str): The root key to filter on.
        definitions (list[Definition]): The list of parsed definitions to search.

    Returns:
        A list of ParedDefinitions with the given root key AaC model definitions.
    """

    def does_definition_root_match(definition: Definition) -> bool:
        return root_key == definition.get_root_key()

    return [definition for definition in definitions if does_definition_root_match(definition)]


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

    matching_definitions = [definition for definition in definitions if does_definition_name_match(definition)]
    matching_definitions_count = len(matching_definitions)

    if matching_definitions_count < 1:
        logging.debug(f"Failed to find a definition with the name '{definition_name}'")

    elif matching_definitions_count > 1:
        matching_definition_names = [definition.name for definition in matching_definitions]
        logging.error(f"Found multiple definitions with the same name '{definition_name}'\n{matching_definition_names}'")

    return matching_definitions[0] if matching_definitions_count >= 1 else None


def convert_parsed_definitions_to_dict_definition(definitions: list[Definition]) -> dict:
    """
    DEPRECATED: Returns a combined dict from the list of Definitions.

    This function is intended only as a stop-gap to support some implementations until they have been fully
    converted to utilize the Definition class instead of python dictionaries.

    """
    return {definition.name: definition.structure for definition in definitions}


def get_definitions_as_yaml(definitions: list[Definition]) -> str:
    """Return all the definitions as a single YAML string."""
    return "\n".join([definition.content for definition in definitions])
