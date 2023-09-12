"""Provide functions for dealing with definition schemas and their relationships."""
import logging
from typing import Optional
from aac.lang.constants import (
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_TYPE,
    DEFINITION_NAME_PRIMITIVES,
)

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
        logging.error(
            f"Failed to find schema definition for '{source_definition.name}' with root key: '{definition_root_key}'."
        )

    return definition_schema


def get_root_schema_definitions(context: LanguageContext) -> dict[str, Definition]:
    """Return a dictionary of root keys to definitions."""
    root_definitions_entries = context.get_root_definitions()

    root_definitions_dict = {}
    for root in root_definitions_entries:
        root_name = root.get_root()
        root_type = root.name

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
            schema_defined_fields = _convert_fields_list_to_dict(schema_definition_fields.get(DEFINITION_FIELD_FIELDS))

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
            field_type = field_dict.get(DEFINITION_FIELD_TYPE)

            if not field_type:
                logging.debug(
                    f"Failed to find the field definition for {field_type} in the defined fields {fields} of '{schema_definition.name}'."
                )

            if context.is_definition_type(field_type) and field_type not in substructure_definitions:
                field_definition = context.get_definition_by_name(field_type)
                substructure_definitions[field_type] = field_definition

                if not field_definition.is_enum():
                    _get_sub_definitions(
                        field_definition, field_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
                    )

    top_level_fields = list(get_schema_defined_fields(source_definition, context).values())
    _get_sub_definitions(source_definition, top_level_fields)
    return list(substructure_definitions.values())


def get_schema_for_field(
    source_definition: Definition, field_keys: list[str], context: LanguageContext
) -> Optional[Definition]:
    """
    Return the schema definition that defines the structure for the field specified by the keys listed in field_keys.

    For example, if you wanted to know the definition for ['model','component'] you'd get 'Field' because components is an array of `Field`.

    Args:
        source_definition (Definition): The definition to search.
        field_keys (list[str]): The list of keys used to identify the target field in the source definition.
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions.

    Returns:
        The schema that defines the field structure, the enum definition defined for an enum field, or the primitives definition for primitive fields.
    """
    keys_to_traverse = field_keys.copy()
    definition_to_return = None

    def _traverse_key(fields: dict) -> Optional[Definition]:
        field_schema_definition = None

        key_to_traverse = keys_to_traverse.pop(0)
        field_to_traverse = fields.get(key_to_traverse, {})

        field_type = str(field_to_traverse.get(DEFINITION_FIELD_TYPE, ""))

        if field_type:
            if context.is_definition_type(field_type):
                field_schema_definition = context.get_definition_by_name(field_type)
                fields_to_traverse = field_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS, {})
                traverse_fields_dict = _convert_fields_list_to_dict(fields_to_traverse)

                if len(keys_to_traverse) > 0 and field_schema_definition:
                    field_schema_definition = _traverse_key(traverse_fields_dict)

            elif context.is_primitive_type(field_type):
                field_schema_definition = context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
            else:
                # Assumed to be enum as enums and primitives are the only terminal types
                field_schema_definition = context.get_enum_definition_by_type(field_type)

        else:
            # In the case of no field-type, we're assumed to be at a terminal value (enum or primitive value)
            field_schema_definition = context.get_enum_definition_by_type(key_to_traverse)

        return field_schema_definition

    if len(keys_to_traverse) > 1:
        keys_to_traverse.pop(0)  # Go ahead and pop the root key since we don't specifically need it.
        definition_to_return = _traverse_key(get_schema_defined_fields(source_definition, context))
    elif len(keys_to_traverse) > 0 and keys_to_traverse[0] == source_definition.get_root_key():
        definition_to_return = get_definition_schema(source_definition, context)

    return definition_to_return


def _convert_fields_list_to_dict(fields: list[dict]) -> dict[str, dict]:
    """Converts the usual list of fields into a dictionary where the field name is the key."""
    return {field.get(DEFINITION_FIELD_NAME): field for field in fields}
