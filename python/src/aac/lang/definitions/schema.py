"""Provide functions for dealing with definition schemas and their relationships."""
import logging
from typing import Optional

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition


def get_definition_schema(source_definition: Definition, context: LanguageContext) -> Optional[Definition]:
    """Return the root definition schema for the source definition."""
    if not isinstance(source_definition, Definition):
        return None

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
                logging.error(f"Failed to find definition named '{root_type}' for root key: {root_name}.")
            else:
                root_definitions_dict[root_name] = root_definition

    return root_definitions_dict


def get_schema_defined_fields(source_definition: Definition, context: LanguageContext) -> dict[str, dict]:
    """Return a dictionary of the schema defined fields where the key is the field name and the value is the field dict."""
    schema_defined_fields = {}
    schema_definition = get_definition_schema(source_definition, context)

    schema_definition_fields = []
    if schema_definition:
        schema_definition_fields = schema_definition.get_top_level_fields()

        if "fields" not in schema_definition_fields:
            logging.error(f"Definition schema '{schema_definition.name}' does not specify any defined fields.")
        else:
            schema_defined_fields = {field.get("name"): field for field in schema_definition_fields.get("fields")}

    else:
        logging.error(f"Failed to find schema for definition key: {source_definition.get_root_key()}")

    return schema_defined_fields


def get_definition_schema_components(source_definition: Definition, context: LanguageContext) -> list[Definition]:
    """
    Return a list of definitions that compose the defined structure of the source definition.

    For example, if a definition is defined as having two fields, one of `Field` type and one of `Behavior` then
    the user can expect the returned list to contain `Field`, `Behavior`, and `Scenario`. `Scenario`
    is not defined as field in the schema, but it is returned because it is a substructure of `Behavior`.

    Args:
        source_definition (Definition): The definition to search through
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A list of dictionaries that match instances of the sub-definition type.
    """
    substructure_definitions = {}

    def _get_sub_definitions(schema_definition: Definition, fields):

        for field_dict in fields:
            field_type = field_dict.get("type")

            if not field_type:
                logging.debug(
                    f"Failed to find the field definition for {field_type} in the defined fields {fields} of '{schema_definition.name}'."
                )

            if context.is_definition_type(field_type) and field_type not in substructure_definitions:
                field_definition = context.get_definition_by_name(field_type)
                substructure_definitions[field_type] = field_definition

                if not field_definition.is_enum():
                    _get_sub_definitions(field_definition, field_definition.get_top_level_fields().get("fields"))

    top_level_fields = list(get_schema_defined_fields(source_definition, context).values())
    _get_sub_definitions(source_definition, top_level_fields)
    return list(substructure_definitions.values())
