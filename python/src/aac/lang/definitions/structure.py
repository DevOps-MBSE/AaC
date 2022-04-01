"""Functions that provide information about the structure of definitions."""

import logging

from aac.lang.context import LanguageContext
from aac.lang.definition_helpers import get_definition_by_name, is_array_type
from aac.lang.definitions.definition import Definition


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

    def _get_substructures(sub_definition: Definition, sub_dict: dict):
        if sub_definition.name == subdefinition_type.name:
            substructure_instances.append(sub_dict)

        sub_definition_defined_fields = sub_definition.get_definition_fields()
        sub_definition_defined_field_names = set(sub_definition_defined_fields.keys())
        populated_field_names = set(sub_dict.keys())

        defined_and_populated_fields = sub_definition_defined_field_names.intersection(populated_field_names)

        for field_name in defined_and_populated_fields:
            field_content = sub_dict.get(field_name)

            # Skip empty fields
            if not field_content:
                continue

            field_type = sub_definition_defined_fields.get(field_name).get("type")

            if context.is_definition_type(field_type):
                field_type_definition = get_definition_by_name(field_type, context.definitions)

                # Enums are like fancy primitives, so we skip them.
                if field_type_definition.is_enum():
                    continue

                field_sub_dicts = field_content

                # If the field type isn't an array type, package it as a one element list.
                if not is_array_type(field_type):
                    field_sub_dicts = [field_content.get(field_name)]

                for field in field_sub_dicts:
                    _get_substructures(field_type_definition, field)

    source_definition_populated_fields = source_definition.get_definition_fields()
    source_definition_root_key = source_definition.get_root_key()
    source_definition_defined_type = get_definition_by_name(source_definition_root_key, context.definitions)
    source_defined_fields = source_definition_defined_type.get_definition_fields()

    if not source_definition_populated_fields:
        logging.debug(f"Failed to find any fields defined in the definition. Definition:\n{source_definition}")
        return []

    for field_name, field_contents in source_definition_populated_fields.items():
        field_content = {field_name: field_contents}
        field_type = source_defined_fields.get(field_name).get("type")

        if not field_type:
            logging.debug(f"Failed to get the field type for {field_content} in the definition: {source_definition.structure}")

        elif context.is_definition_type(field_type):
            field_type_definition = get_definition_by_name(field_type, context.definitions)
            field_sub_dicts = field_content.get(field_name)

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

    def _get_sub_definitions(sub_definition: Definition):

        defined_fields = sub_definition.get_definition_fields()

        for field_name in defined_fields.keys():
            field_type_name = defined_fields.get(field_name).get("type") or None

            if not field_type_name:
                logging.debug(f"Failed to find the field definition for {field_name} in the defined fields {defined_fields}.\nDefinition{sub_definition.structure}")

            elif field_type_name not in substructure_definitions and context.is_definition_type(field_type_name):
                field_type_definition = get_definition_by_name(field_type_name, context.definitions)
                substructure_definitions[field_type_name] = field_type_definition

                if not field_type_definition.is_enum():
                    _get_sub_definitions(field_type_definition)

    source_definition_root_key = source_definition.get_root_key()
    source_definition_type_definition = get_definition_by_name(source_definition_root_key, context.definitions)
    defined_source_definition_fields = source_definition_type_definition.get_definition_fields()

    # Loop through the Field[] definitions in the defining type.
    for field_name in defined_source_definition_fields.keys():
        field_type = defined_source_definition_fields.get(field_name).get("type")

        if context.is_definition_type(field_type):
            field_definition = get_definition_by_name(field_type, context.definitions)
            substructure_definitions[field_type] = field_definition
            _get_sub_definitions(field_definition)

    return list(substructure_definitions.values())
