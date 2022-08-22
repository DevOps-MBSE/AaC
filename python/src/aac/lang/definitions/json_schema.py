"""Common JsonSchema Functions for AaC Definitions."""
import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.type import remove_list_type_indicator, is_array_type
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema


def get_definition_json_schema(definition: Definition, language_context: LanguageContext) -> dict:
    """
    Return a string containing the JSON Schema for the definition; the definition's schema definition is converted to the JSON schema.

    Args:
        definition (Definition): The definition to convert to JSON Schema

    Returns:
        a dictionary containing the definition as a JSON schema for the definition's content.
    """

    definition_schema = get_definition_schema(definition, language_context)

    schema_dict = {}
    if definition_schema is None:
        logging.error(f"Failed to find the definition schema for {definition.name}")
    else:
        schema_dict = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": _get_definition_json_schema(definition_schema, language_context),
        }

    return schema_dict


def _get_definition_json_schema(definition_schema: Definition, language_context: LanguageContext) -> dict:
    """Return the json schema structure for the definition schema."""

    schema_object = {}
    schema_structure_fields = definition_schema.get_top_level_fields().get("fields", {})
    for field in schema_structure_fields:
        field_name = field.get("name")
        field_type = field.get("type")

        if field_type is None:
            logging.error(f"Field entry {field_name} is missing type declaration in schema {definition_schema.name}")
        else:
            if language_context.is_definition_type(field_type) or language_context.is_primitive_type(field_type):
                field_json_schema = _get_definition_field_json_schema(field_name, field_type, language_context)
                schema_object.update(field_json_schema)
            else:
                logging.warning(
                    f"Excluding field {field_name} because there is no corresponding schema definition could be found for type {field_type}."
                )

    return schema_object


def _get_definition_field_json_schema(field_name: str, field_type: str, language_context: LanguageContext) -> dict:
    json_schema_fragment = {}
    if language_context.is_primitive_type(field_type):
        json_schema_fragment = _get_primitive_field_json_schema(field_name, field_type)

    elif language_context.is_enum_type(field_type):
        json_schema_fragment = _get_enum_field_json_schema(field_name, field_type, language_context)

    elif language_context.is_definition_type(field_type):
        json_schema_fragment = _get_defined_type_field_json_schema(field_name, field_type, language_context)

    else:
        logging.error(f"Field entry {field_name} is not a definition, primitive, or enum type declaration.")

    return json_schema_fragment


def _get_defined_type_field_json_schema(field_name: str, field_type: str, language_context: LanguageContext) -> dict:
    """Return the JSON schema for a definition field."""
    is_field_structure_an_array = is_array_type(field_type)

    schema_object = {}
    field_schema = language_context.get_definition_by_name(field_type)

    if field_schema is not None:
        defined_fields = field_schema.get_top_level_fields().get("fields", {})
        schema_sub_structures = {}

        for field in defined_fields:
            defined_field_name = field.get("name")
            defined_field_type = field.get("type")
            schema_sub_structures.update(
                _get_definition_field_json_schema(defined_field_name, defined_field_type, language_context)
            )

    if is_field_structure_an_array:
        schema_object = {field_name: {"type": "array", "items": {"type": "object", "properties": schema_sub_structures}}}
    else:
        schema_object = {field_name: {"type": "object", "properties": schema_sub_structures}}

    return schema_object


def _get_primitive_field_json_schema(field_name: str, field_type: str) -> dict:
    """
    Return the JSON schema for a primitive field.

    example return value:

    Primitive value:
    ```
    "name": {
        "type": "string"
    }
    ```

    Primitives array:
    ```
    "names": {
        "type": "array",
        "items": {
            "type": "string"
        }
    }
    ```
    """
    primitive_field_schema = {}
    sanitized_type = remove_list_type_indicator(field_type)

    if is_array_type(field_type):
        primitive_field_schema = {field_name: {"type": "array", "items": {"type": sanitized_type}}}
    else:
        primitive_field_schema = {field_name: {"type": sanitized_type}}

    return primitive_field_schema


def _get_enum_field_json_schema(field_name: str, field_type: str, language_context: LanguageContext) -> dict:
    """
    Return the JSON schema for an enum field.

    example return value:
    ```
    "name": {
            "type": "string",
            "enum": ["John", "Jane", "Junior"]
    }
    ```
    """
    enum_definition = language_context.get_definition_by_name(field_type)
    enum_schema_segment = {}

    if enum_definition:
        enum_values = enum_definition.get_top_level_fields().get("values", [])
        enum_schema_segment = {field_name: {"type": "string", "enum": enum_values}}
    else:
        logging.warn(f"There is no enum definition in the context named {field_type}")

    return enum_schema_segment
