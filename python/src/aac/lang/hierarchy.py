"""Provides utilities to manage and navigate the hierarchy of definitions."""
import logging
from typing import Optional

from aac.lang.constants import (
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_TYPE,
    DEFINITION_NAME_ROOT,
    DEFINITION_NAME_SCHEMA,
)
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition


def get_definition_ancestry(definition: Definition, context: LanguageContext) -> list[Definition]:
    """Return an ordered list of ancestor definitions starting with the root definition and ending with the argument."""

    ancestors_list = []
    found_self_defined_ancestor = False
    ancestor_definition: Optional[Definition] = definition

    # If the definition key isn't defined, return the schema definition as the only ancestor.
    if definition.get_root_key() not in context.get_root_keys():
        ancestors_list.append(get_root_definition_by_key(DEFINITION_NAME_SCHEMA, context.definitions))
        found_self_defined_ancestor = True

    # Loop until we get to the root definition defining itself.
    while not found_self_defined_ancestor and ancestor_definition:
        found_self_defined_ancestor = ancestor_definition.name == ancestor_definition.get_root_key()
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
    root_definition = get_definition_by_name(DEFINITION_NAME_ROOT, parsed_definitions)
    root_fields = search_definition(root_definition, [DEFINITION_NAME_SCHEMA, DEFINITION_FIELD_FIELDS])

    root_key_fields = list(filter(lambda field: (field.get(DEFINITION_FIELD_NAME) == root_key), root_fields))
    root_key_count = len(root_key_fields)

    root_key_field = None
    if root_key_count < 1:
        logging.error(f"Failed to find field based on root key.\nField name: {root_key}\nAvailable Fields:{root_fields}")
    else:
        root_key_field = root_key_fields[0]

        if root_key_count > 1:
            logging.error(
                f"Found multiple fields when only expected to find one.\nField name: {root_key}\nReturned Fields:{root_key_fields}"
            )

        return get_definition_by_name(root_key_field.get(DEFINITION_FIELD_TYPE), parsed_definitions)
