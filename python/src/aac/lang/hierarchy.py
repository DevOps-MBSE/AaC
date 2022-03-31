"""Provides utilities to manage and navigate the hierarchy of definitions."""

import logging
from typing import Optional

from aac.lang.context import LanguageContext
from aac.lang.definition_helpers import get_definition_by_name, search_definition
from aac.lang.definitions.definition import Definition


def get_definition_ancestry(definition: Definition, context: LanguageContext) -> list[Definition]:
    """Return an ordered list of ancestor definitions starting with the root definition and ending with the argument."""

    ancestors_list = []
    found_self_defined_ancestor = False
    ancestor_definition = definition

    # Loop until we get to the root definition defining itself.
    while not found_self_defined_ancestor:
        found_self_defined_ancestor = (ancestor_definition.name == ancestor_definition.get_root_key())
        ancestors_list.append(ancestor_definition)
        ancestor_definition = get_root_definition_by_key(ancestor_definition.get_root_key(), context.definitions)

    ancestors_list.reverse()
    return ancestors_list


def get_root_definition_by_key(root_key: str, parsed_definitions: list[Definition]) -> Optional[Definition]:
    """
    Return the parsed definition that defines a root key structure or None if not found.

    Args:
        root_key (str): The root key from a Definition
        parsed_definitions (list[Definition]): A list of definitions to search, must include the root Definition.

    Return:
        An optional Definition that defines the structure of the root key.
    """
    root_definition = get_definition_by_name("root", parsed_definitions)
    root_fields = search_definition(root_definition, ["data", "fields"])

    root_key_fields = list(filter(lambda field: (field.get("name") == root_key), root_fields))
    root_key_count = len(root_key_fields)

    root_key_field = None
    if root_key_count < 1:
        logging.error(f"Failed to find field based on root key.\nField name: {root_key}\nAvailable Fields:{root_fields}")
    else:
        root_key_field = root_key_fields[0]

        if root_key_count > 1:
            logging.error(f"Found multiple fields when only expected to find one.\nField name: {root_key}\nReturned Fields:{root_key_fields}")

    return get_definition_by_name(root_key_field.get("type"), parsed_definitions)
