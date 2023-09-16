"""Provides utilities to manage and navigate the hierarchy of definitions."""
import logging
from typing import Optional

from aac.lang.constants import ROOT_KEY_SCHEMA
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
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

    ancestors_list: list[Definition] = []

    # If the definition key isn't defined, return an empty ancestor list.
    if definition.get_root_key() not in context.get_root_keys():
        # I finally figured out why this is here.  It's because we're using Schema as a hack to hold a list of "Global Validator" declarations.
        ancestors_list.append(get_root_definition_by_key(ROOT_KEY_SCHEMA, context))
        logging.error(f"The definition '{definition.name}' does not have a defined root key '{definition.get_root_key()}'.")
    else:
        found_self_defined_ancestor = False
        ancestor_definition: Optional[Definition] = definition

        # Loop until we get to `Schema` defining itself.
        while not found_self_defined_ancestor and ancestor_definition:
            ancestor_root_schema = get_definition_schema(ancestor_definition, context)
            found_self_defined_ancestor = ancestor_definition == ancestor_root_schema
            ancestors_list.append(ancestor_definition)
            ancestor_definition = get_root_definition_by_key(ancestor_definition.get_root_key(), context)

    ancestors_list.reverse()
    return ancestors_list


def get_root_definition_by_key(root_key: str, context: LanguageContext) -> Optional[Definition]:
    """
    Return the definition that defines the structure of the root key.

    This function is useful for looking up the schema definition that defines a root key. For instance, if you
    passed the root key 'model' and the definitions list contains the Root and Model definitions, then this
    function will return the Model definition.

    Args:
        root_key (str): The root key to search for
        context (LanguageContext):  The AaC language context containing the definitions to search through.

    Return:
        A Definition that defines the structure of the root key, or None if not found.
    """

    if root_key in context.get_root_keys():
        root_key_definition, *_ = [definition for definition in context.get_root_definitions() if root_key == definition.get_root()]
        return root_key_definition
    else:
        logging.error(f"Failed to find root key.\nRoot Key to find: {root_key}\nAvailable Fields:{context.get_root_keys()}")
        return None
