"""Arch-as-Code helper functions to simplify managing and working with parsed definitions/models."""

import logging
from typing import Any, Optional

from aac.parser import ParsedDefinition


def search(model: dict[str, Any], search_keys: list[str]) -> list:
    """
    Search an AaC model structure by key(s).

    Searches a dict for the contents given a set of keys. Search returns a list of
    the entries in the model that correspond to those keys.  This search will
    traverse the full dict tree, including embedded lists.

        Typical usage example:
        Let's say you have a dict structure parsed from the following AaC yaml.

            data:
            name: MyData
            fields:
                - name: one
                type: string
                - name: two
                type: string
            required:
                - one

        You know the structure of the specification and need to iterate through each field.
        The search utility method simplifies that for you.

            for field in definition_helpers.search(my_model, ["data", "fields"]):
                print(f"field_name: {field["name"]} field_type {field["type"]}")

        The above example demonstrates a complex type being returned as a dict.  Search will also
        provide direct access to simple types in the model.

            for field_name in definition_helpers.search(my_model, ["data", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        model: The model to search.  This is often the value taken from the dict returned
            by aac.parser.parse(<aac_file>).
        search_keys: A list of strings representing keys in the model dict hierarchy.

    Returns:
        Returns a list of found data items based on the search keys.

    """

    done = False
    ret_val = []

    keys = search_keys.copy()
    # first make sure there is a key to search for
    if len(keys) == 0 or not isinstance(model, dict):
        logging.error(f"invalid arguments: {keys}, {type(model)}")
        return []

    search_key = keys.pop(0)
    final_key = len(keys) == 0
    model_value = None

    # see if the key exists in the dict
    if search_key in model:
        model_value = model[search_key]

        if final_key:
            if isinstance(model_value, list):
                ret_val = model_value
                done = True
            else:
                ret_val.append(model_value)
                done = True

    # it isn't the final key and the value is a dict, so continue searching
    if not done and isinstance(model_value, dict):
        if isinstance(model_value, dict):
            ret_val = search(model[search_key], keys)
            done = True

    # it isn't the final key and the value is a list, so search each value
    if not done and isinstance(model_value, list):
        for model_item in model_value:

            if isinstance(model_item, dict):
                ret_val = ret_val + (search(model_item, keys))
            else:
                logging.error("keys exceeds depth of the dict to search")
                done = True
        done = True

    # not an error, just zero results
    else:
        logging.info(f"keys[{search_keys}] not found in model")
        done = True

    return ret_val


def search_definition(parsed_definition: ParsedDefinition, search_keys: list[str]) -> list:
    """
    Search an AaC definition structure by key(s).

    Searches a ParsedDefinition for a subset of the definition contents given a set of keys.
    Search returns a list of  entries in the definition that correspond to those keys. This search
    will traverse the entire parsed definition's structure.

        Typical usage example:
        Let's say you have a definition structure parsed from the following AaC yaml.

            data:
            name: MyData
            fields:
                - name: one
                type: string
                - name: two
                type: string
            required:
                - one

        You know the structure of the specification and need to iterate through each field.
        The search utility method simplifies that for you.

            for field in definition_helpers.search(my_model, ["data", "fields"]):
                print(f"field_name: {field["name"]} field_type {field["type"]}")

        The above example demonstrates a complex type being returned as a dict.  Search will also
        provide direct access to simple types in the model.

            for field_name in definition_helpers.search(my_definition, ["data", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        model: The definition to search.  This is often the value taken from the dict returned
            by aac.parser.parse(<aac_file>).
        search_keys: A list of strings representing keys in the model dict hierarchy.

    Returns:
        Returns a list of found data items based on the search keys.

    """

    return search(parsed_definition.definition, search_keys)


def get_models_by_type(models: dict[str, dict], root_name: str) -> dict[str, dict]:
    """Gets subset of models of a specific root name.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed models to be "filtered" to a specific root name.

    Args:
        models: The dict of models to search.
        root_name: The root name to filter on.

    Returns:
        A dict mapping type names to AaC model definitions.
    """
    ret_val = {}
    for key, value in models.items():
        if root_name in value.keys():
            ret_val[key] = value

    return ret_val


def get_definitions_by_root_key(parsed_definitions: list[ParsedDefinition], root_key: str) -> list[ParsedDefinition]:
    """Return a subset of definitions with the given root key.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed definitions to be "filtered" to a specific root name.

    Args:
        parsed_definitions: The list of parsed definitions to search.
        root_key: The root key to filter on.

    Returns:
        A list of ParedDefinitions with the given root key AaC model definitions.
    """

    def does_definition_root_match(parsed_definition: ParsedDefinition) -> bool:
        return root_key == parsed_definition.get_root_key()

    return list(filter(does_definition_root_match, parsed_definitions))


def get_definition_by_name(parsed_definitions: list[ParsedDefinition], definition_name: str) -> Optional[ParsedDefinition]:
    """Get a definition of models of a specific root name.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed models to be "filtered" to a specific root name.

    Args:
        models: The dict of models to search.
        definition_name: The definition's name to locate.

    Returns:
        A ParsedDefinition with the given name or None.
    """

    def does_definition_name_match(parsed_definition: ParsedDefinition) -> bool:
        return remove_list_type_indicator(definition_name) == parsed_definition.name

    matching_definitions = list(filter(does_definition_name_match, parsed_definitions))
    matching_definitions_count = len(matching_definitions)

    result = None
    if (matching_definitions_count > 1):
        logging.error("Found multiple definitions with the same name \"{definition_name}\"\n{matching_definitions}\"")
        raise RuntimeError(f"Found multiple definitions with the same name \"{definition_name}\"\n{matching_definitions}")

    elif (matching_definitions_count < 1):
        logging.debug("Failed to find a definition with the name \"{definition_name}\"")

    else:
        result = matching_definitions[0]

    return result


def convert_parsed_definitions_to_dict_definition(parsed_definitions: list[ParsedDefinition]) -> dict:
    """
    DEPRECATED: Returns a combined dict from the list of ParsedDefinitions.

    This function is intended only as a stop-gap to support some implementations until they have been fully
    converted to utilize ParsedDefinitions.
    """
    return {definition.name: definition.definition for definition in parsed_definitions}


def remove_list_type_indicator(list_type: str) -> str:
    """Return the AaC type without any trailing list indicator characters '[]'."""
    return list_type.split("[]")[0]


def is_array_type(type: str) -> bool:
    """Returns a boolean indicating if the field is an array of multiple entries."""
    return type.endswith("[]")


def get_definition_fields_and_types(parsed_definition: ParsedDefinition, context_definitions: list[ParsedDefinition]) -> dict[str, ParsedDefinition]:
    """Return a list of field names to their definition types."""
    definition_structure = get_definition_by_name(context_definitions, parsed_definition.get_root_key())
    defined_fields = search_definition(definition_structure, [definition_structure.get_root_key(), "fields"])

    field_types = {}
    for field in defined_fields:
        field_name = field.get("name")
        field_type = field.get("type")

        type_definition = get_definition_by_name(context_definitions, field_type) or field_type
        field_types = field_types | {field_name: type_definition}

    return field_types
