"""Provides utilities to manage and navigate the hierarchy of definitions."""
import logging
from typing import Optional

from aac.lang.constants import (
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_TYPE,
    DEFINITION_NAME_ROOT,
    ROOT_KEY_SCHEMA,
)
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.lang.definitions.schema import get_definition_schema


def get_definition_ancestry(definition: Definition, context: LanguageContext) -> list[Definition]:
    """
    Return an ordered list of ancestor definitions starting with the root definition and ending with the argument.

    This function traverses the list of the definition's schema definitions all the way back to `Schema`. For instance,
    if you passed a `model` root key definition to this function, it would return itself, the `Model` definition, and
    the `Schema` definition. This is because a definition with the `model` root key is defined by the schema `Model` definition
    which is in turn defined by the `Schema` definition.

    Args:
        definition (Definition): The definition to search for ancestors of.
        context (LanguageContext): The language context containing the definition's schema.

    Returns:
        A list of definitions that define the schema and the schema's parent schemas.
    """

    ancestors_list = []

    # If the definition key isn't defined, return an empty ancestor list.
    if definition.get_root_key() not in context.get_root_keys():
        ancestors_list.append(get_root_definition_by_key(ROOT_KEY_SCHEMA, context.definitions))
        logging.error(f"The definition '{definition.name}' does not have a defined root key '{definition.get_root_key()}'.")
    else:
        found_self_defined_ancestor = False
        ancestor_definition: Optional[Definition] = definition

        # Loop until we get to `Schema` defining itself.
        while not found_self_defined_ancestor and ancestor_definition:
            ancestor_root_schema = get_definition_schema(ancestor_definition, context)
            found_self_defined_ancestor = ancestor_definition == ancestor_root_schema
            ancestors_list.append(ancestor_definition)
            ancestor_definition = get_root_definition_by_key(ancestor_definition.get_root_key(), context.definitions)

    ancestors_list.reverse()
    return ancestors_list


def get_root_definition_by_key(root_key: str, definitions: list[Definition]) -> Optional[Definition]:
    """
    Return the definition that defines the structure of the root key.

    This function is useful for looking up the schema definition that defines a root key. For instance, if you
    passed the root key 'model' and the definitions list contains the Root and Model definitions, then this
    function will return the Model definition.

    Args:
        root_key (str): The root key to search for
        definitions (list[Definition]): A list of definitions to search, must include the root Definition.

    Return:
        A Definition that defines the structure of the root key, or None if not found.
    """
    root_definition = get_definition_by_name(DEFINITION_NAME_ROOT, definitions)
    root_fields = search_definition(root_definition, [ROOT_KEY_SCHEMA, DEFINITION_FIELD_FIELDS])

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

        return get_definition_by_name(root_key_field.get(DEFINITION_FIELD_TYPE), definitions)
