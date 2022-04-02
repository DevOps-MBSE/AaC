"""Functions that provide information about the structure of definitions."""

import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.arrays import is_array_type
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_schema_defined_fields


def get_substructures_by_type(source_definition: Definition, subdefinition_type: Definition, context: LanguageContext) -> list[dict]:
    """
    Return a list of dictionaries that represent instances of the sub-definition type within the definition under search.

    For example, if a definition of type `model` where to be searched for every instance of the `Field` type,
    then every instance of a `Field` definition within the `model` definition will be returned. This includes embedded
    fields, such as any instances of `Field` the might be defined in the `model` under the `Behavior` definition.

    Args:
        source_definition (Definition): The definition to search through
        subdefinition_type (Definition): The definition for the type
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A list of dictionaries that match instances of the sub-definition type.
    """
    substructure_instances = []

    def _get_substructures(sub_schema_definition: Definition, sub_dict: dict):
        if sub_schema_definition.name == subdefinition_type.name:
            substructure_instances.append(sub_dict)

        sub_definition_defined_fields = sub_schema_definition.get_fields().get("fields")
        sub_definition_fields_dict = {field.get("name"): field for field in sub_definition_defined_fields}
        sub_definition_defined_field_names = set(sub_definition_fields_dict.keys())
        populated_field_names = set(sub_dict.keys())

        defined_and_populated_fields = sub_definition_defined_field_names.intersection(populated_field_names)

        for field_name in defined_and_populated_fields:
            field_content = sub_dict.get(field_name)

            # Skip empty fields
            if not field_content:
                continue

            field_type = sub_definition_fields_dict.get(field_name).get("type")

            if context.is_definition_type(field_type):
                field_type_definition = context.get_definition_by_name(field_type)

                # Enums are like fancy primitives, so we skip them.
                if field_type_definition.is_enum():
                    continue

                field_sub_dicts = field_content

                # If the field type isn't an array type, package it as a one element list.
                if not is_array_type(field_type):
                    field_sub_dicts = [field_content.get(field_name)]
                elif not type(field_sub_dicts) is list:
                    logging.error(f"Value '{field_sub_dicts}' is not an array type like its defined type '{field_type}'. Bad value in the field '{field_name}' in definition '{source_definition.name}'.")
                    continue

                for field in field_sub_dicts:
                    _get_substructures(field_type_definition, field)

    populated_fields = source_definition.get_fields()
    source_definition_root_key = source_definition.get_root_key()

    # Return the whole definition dictionary if the desired substructure is equal to the root type.
    if source_definition_root_key == subdefinition_type.name:
        return [source_definition.structure.get(source_definition_root_key)]

    defined_fields = get_schema_defined_fields(source_definition, context)

    for field_name, field_contents in populated_fields.items():
        field_type = defined_fields.get(field_name).get("type")

        if not field_type:
            logging.debug(f"Failed to get the field type for {field_contents} in the definition: {source_definition.structure}")

        elif context.is_definition_type(field_type):
            field_type_definition = context.get_definition_by_name(field_type)
            field_sub_dicts = field_contents

            if not is_array_type(field_type):
                field_sub_dicts = [field_sub_dicts]

            for field in field_sub_dicts:
                _get_substructures(field_type_definition, field)

    return substructure_instances


def get_sub_definitions(source_definition: Definition, context: LanguageContext) -> list[Definition]:
    """
    Return a list definitions that make up the structure of the source definition.

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

    def _get_sub_definitions(sub_schema_definition: Definition):

        defined_fields = sub_schema_definition.get_fields().get("fields") or []

        for field_dict in defined_fields:
            field_type = field_dict.get("type")

            if not field_type:
                logging.debug(f"Failed to find the field definition for {field_type} in the defined fields {defined_fields} of '{sub_schema_definition.name}'.")

            if context.is_definition_type(field_type) and field_type not in substructure_definitions:
                field_definition = context.get_definition_by_name(field_type)
                substructure_definitions[field_type] = field_definition

                if not field_definition.is_enum():
                    _get_sub_definitions(field_definition)

    defined_source_fields = get_schema_defined_fields(source_definition, context)

    for field_name in defined_source_fields.keys():
        field_dict = defined_source_fields.get(field_name)
        field_type = field_dict.get("type")

        if context.is_definition_type(field_type):
            field_definition = context.get_definition_by_name(field_type)
            substructure_definitions[field_type] = field_definition
            _get_sub_definitions(field_definition)

    return list(substructure_definitions.values())
