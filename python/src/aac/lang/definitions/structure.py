"""Functions that provide information about the structure of definitions."""
import logging

from aac.lang.definitions.type import is_array_type, remove_list_type_indicator
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema
from aac.lang.language_context import LanguageContext


def get_substructures_by_type(
    source_definition: Definition, target_schema_definition: Definition, context: LanguageContext
) -> list[dict]:
    """
    Return a list of dictionaries that represent instances of the sub-definition type within the source definition.

    For example, if a definition of type `model` were to be searched for every instance of the `Field` type,
    then every instance of a `Field` definition within the `model` definition will be returned. This includes embedded
    fields, such as any instances of `Field` the might be defined in the `model` under the `Behavior` definition.

    Args:
        source_definition (Definition): The definition to search through
        target_schema_definition (Definition): Defines the target schema to extract from the source definition
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A list of dictionaries that match instances of the sub-definition schema.
    """
    substructure_instances = []

    def _get_substructures(schema_definition: Definition, definition_dict: dict):
        if schema_definition.name == target_schema_definition.name:
            substructure_instances.append(definition_dict)

        schema_defined_fields = schema_definition.get_top_level_fields().get("fields") or []
        schema_defined_fields_dict = {field.get("name"): field for field in schema_defined_fields}
        field_names_to_traverse = set(schema_defined_fields_dict.keys()).intersection(set(definition_dict.keys()))

        for field_name in sorted(field_names_to_traverse):
            field_type = schema_defined_fields_dict.get(field_name).get("type")
            field_schema_definition = context.get_definition_by_name(field_type)

            if field_schema_definition and not field_schema_definition.is_enum():
                field_content = definition_dict.get(field_name) or []

                # If the field type isn't an array type, package it as a one element list.
                if not is_array_type(field_type):
                    field_content = [field_content]
                elif not type(field_content) is list:
                    logging.error(
                        f"Value '{field_content}' is not an array type like its defined type '{field_type}'. Bad value in the field '{field_name}' in definition '{source_definition.name}'."
                    )
                    continue

                fields_to_traverse = [field for field in field_content if isinstance(field, dict)]
                for field in fields_to_traverse:
                    _get_substructures(field_schema_definition, field)

    source_definition_root_key = source_definition.get_root_key()
    source_definition_fields = source_definition.get_top_level_fields()

    # Return the whole definition dictionary if the desired substructure is the root type.
    if source_definition_root_key == target_schema_definition.name:
        substructure_instances = [source_definition_fields]
    else:
        source_definition_schema = get_definition_schema(source_definition, context)

        if source_definition_schema:
            _get_substructures(source_definition_schema, source_definition_fields)
        else:
            logging.error(f"Failed to find a schema definition for the key {source_definition_root_key}.")

    return substructure_instances


def strip_undefined_fields_from_definition(definition: Definition, context: LanguageContext) -> Definition:
    """
    Strip any fields that aren't defined in the definition's schema and returns a stripped copy of the definition.

    Args:
        definition (Definition): The definition to strip undefined fields from
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A copy of the original definition with undefined fields removed.
    """

    def _strip_fields(definition_dict: dict, dict_schema: Definition):
        defined_top_level_fields = dict_schema.get_top_level_fields().get("fields", {})
        defined_top_level_fields_dict = {field.get("name"): field for field in defined_top_level_fields}
        definition_dict_field_names = list(definition_dict.keys())

        for field_name in definition_dict_field_names:
            if field_name not in defined_top_level_fields_dict:
                logging.info(f"Removing undefined field {field_name} from definition: {definition.name}")
                del definition_dict[field_name]
            else:
                field_schema_type = defined_top_level_fields_dict.get(field_name).get("type")
                is_array_field = is_array_type(field_schema_type)

                field_schema = context.get_definition_by_name(remove_list_type_indicator(field_schema_type))

                if field_schema and not context.is_enum_type(field_schema_type):
                    field_sub_dict = definition_dict.get(field_name, {})
                    field_dicts = [entry for entry in field_sub_dict] if is_array_field else [field_sub_dict]

                    for field_sub_dict in field_dicts:
                        _strip_fields(field_sub_dict, field_schema)

    if definition:
        stripped_definition = definition.copy()
        definition_schema = get_definition_schema(definition, context)
        definition_structure = stripped_definition.get_top_level_fields()
        _strip_fields(definition_structure, definition_schema)
        return stripped_definition
