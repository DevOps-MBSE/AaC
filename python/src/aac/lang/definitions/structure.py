"""Functions that provide information about the structure of definitions."""

import logging

from aac.lang.definitions.arrays import is_array_type
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema, get_schema_defined_fields
from aac.lang.language_context import LanguageContext


def get_substructures_by_type(
    source_definition: Definition, sub_schema_definition: Definition, context: LanguageContext
) -> list[dict]:
    """
    Return a list of dictionaries that represent instances of the sub-definition type within the source definition.

    For example, if a definition of type `model` where to be searched for every instance of the `Field` type,
    then every instance of a `Field` definition within the `model` definition will be returned. This includes embedded
    fields, such as any instances of `Field` the might be defined in the `model` under the `Behavior` definition.

    Args:
        source_definition (Definition): The definition to search through
        sub_schema_definition (Definition): Defines the target schema to extract from the source definition
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A list of dictionaries that match instances of the sub-definition schema.
    """
    substructure_instances = []

    def _get_substructures(schema_definition: Definition, definition_dict: dict):
        if schema_definition.name == sub_schema_definition.name:
            substructure_instances.append(definition_dict)

        schema_defined_fields = schema_definition.get_fields().get("fields")
        schema_defined_fields_dict = {field.get("name"): field for field in schema_defined_fields}
        field_names_to_traverse = set(schema_defined_fields_dict.keys()).intersection(set(definition_dict.keys()))

        for field_name in sorted(field_names_to_traverse):
            field_type = schema_defined_fields_dict.get(field_name).get("type")

            if context.is_definition_type(field_type):
                field_type_definition = context.get_definition_by_name(field_type)
                field_content = definition_dict.get(field_name)

                # Skip empty fields and enums
                if not field_content or field_type_definition.is_enum():
                    continue
                # If the field type isn't an array type, package it as a one element list.
                if not is_array_type(field_type):
                    field_content = [field_content]
                elif not type(field_content) is list:
                    logging.error(
                        f"Value '{field_content}' is not an array type like its defined type '{field_type}'. Bad value in the field '{field_name}' in definition '{source_definition.name}'."
                    )
                    continue

                for field in field_content:
                    _get_substructures(field_type_definition, field)

    source_definition_root_key = source_definition.get_root_key()
    source_definition_fields = source_definition.get_fields()

    # Return the whole definition dictionary if the desired substructure is the to the root type.
    if source_definition_root_key == sub_schema_definition.name:
        substructure_instances = [source_definition_fields]
    else:
        source_definition_schema = get_definition_schema(source_definition, context)
        _get_substructures(source_definition_schema, source_definition_fields)

    return substructure_instances


def get_sub_definitions(source_definition: Definition, context: LanguageContext) -> list[Definition]:
    """
    Return a list schema definitions that make up the structure of the source definition.

    For example, if a definition has two fields, one of `Field` type and one of `Behavior` then
    the user can expect the returned list to contain `Field`, `Behavior`, and `Scenario`. `Scenario`
    is also returned because it is a substructure of `Behavior`.

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
                    _get_sub_definitions(field_definition, field_definition.get_fields().get("fields"))

    top_level_fields = list(get_schema_defined_fields(source_definition, context).values())
    _get_sub_definitions(source_definition, top_level_fields)
    return list(substructure_definitions.values())
