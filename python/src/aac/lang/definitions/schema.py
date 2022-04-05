"""Provide functions for dealing with definition schemas and their relationships."""
import logging
from typing import Optional

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition


def get_definition_schema(source_definition: Definition, context: LanguageContext) -> Optional[Definition]:
    """Return the root definition schema for the source definition."""
    root_schema_definitions = get_root_schema_definitions(context)
    definition_root_key = source_definition.get_root_key()
    definition_schema = root_schema_definitions.get(definition_root_key)

    if not definition_schema:
        logging.error(f"Failed to find schema definition for '{source_definition.name}' with root key: '{definition_root_key}'.")

    return definition_schema


def get_root_schema_definitions(context: LanguageContext) -> dict[str, Definition]:
    """Return a dictionary of root keys to definitions."""
    root_definitions_entries = context.get_root_fields()

    root_definitions_dict = {}
    for root in root_definitions_entries:
        root_name = root.get("name")
        root_type = root.get("type")

        # We only care about definitions, which excludes primitive types
        if context.is_definition_type(root_type):
            root_definition = context.get_definition_by_name(root_type)

            if not root_definition:
                logging.error(f"Failed to find defintion named '{root_type}' for root key: {root_name}.")
            else:
                root_definitions_dict[root_name] = root_definition

    return root_definitions_dict


def get_schema_defined_fields(source_definition: Definition, context: LanguageContext) -> dict[str, dict]:
    """Return a dictionary of the schema defined fields where the key is the field name and the value is the field dict."""
    schema_defined_fields = {}
    schema_defintion = get_definition_schema(source_definition, context)
    schema_definition_fields = schema_defintion.get_fields()

    if "fields" not in schema_definition_fields:
        logging.error(f"Definition schema '{schema_defintion.name}' does not specify any defined fields.")
    else:
        schema_defined_fields = {field.get("name"): field for field in schema_definition_fields.get("fields")}

    return schema_defined_fields
