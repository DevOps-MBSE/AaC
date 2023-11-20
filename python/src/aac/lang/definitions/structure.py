"""Functions that provide information about the structure of definitions."""
import logging

from aac.lang.constants import DEFINITION_FIELD_FIELDS, DEFINITION_FIELD_NAME, DEFINITION_FIELD_TYPE
from aac.lang.definitions.type import is_array_type, remove_list_type_indicator
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema
from aac.lang.language_context import LanguageContext


def get_substructures_by_type(
    source_definition: Definition, target_schema_definition: Definition, context: LanguageContext   # POPO update
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

    def _get_substructures(schema_definition: Definition, definition_dict: dict):   # POPO update
        if schema_definition.name == target_schema_definition.name:   # POPO update
            substructure_instances.append(definition_dict)  # POPO update

        schema_defined_fields = schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS) or []   # POPO update
        schema_defined_fields_dict = {field.get(DEFINITION_FIELD_NAME): field for field in schema_defined_fields}   # POPO update
        field_names_to_traverse = set(schema_defined_fields_dict.keys()).intersection(set(definition_dict.keys()))  # POPO update

        for field_name in sorted(field_names_to_traverse):
            field_type = schema_defined_fields_dict.get(field_name).get(DEFINITION_FIELD_TYPE)  # POPO update
            field_schema_definition = context.get_definition_by_name(field_type)    # POPO update

            if field_schema_definition and not field_schema_definition.is_enum():   # POPO update
                field_content = definition_dict.get(field_name) or []   # POPO update

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
                    _get_substructures(field_schema_definition, field)  # POPO update

    source_definition_root_key = source_definition.get_root_key()   # POPO update
    source_definition_fields = source_definition.get_top_level_fields()   # POPO update

    # Return the whole definition dictionary if the desired substructure is the root type.
    if source_definition_root_key == target_schema_definition.name:   # POPO update
        substructure_instances = [source_definition_fields]   # POPO update
    else:
        source_definition_schema = get_definition_schema(source_definition, context)    # POPO update

        if source_definition_schema:    # POPO update
            _get_substructures(source_definition_schema, source_definition_fields)  # POPO update
        else:
            logging.error(f"Failed to find a schema definition for the key {source_definition_root_key}.")  # POPO update

    return substructure_instances


def get_fields_by_enum_type(source_definition: Definition, target_enum_type: Definition, context: LanguageContext) -> list[dict]:   # POPO update
    """
    Return a list of dictionaries that represent instances of fields with the target enum type within the source definition.

    For example, if a definition of type `model` were to be searched for every instance of the `BehaviorType` enum type,
    then every instance of a field typed as `BehaviorType` within the `model` definition will be returned.

    Args:
        source_definition (Definition): The definition to search through
        target_enum_type (Definition): Defines the field enum type to extract from the source definition
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A list of dictionaries that match instances of the enum type.
    """
    field_dicts = []

    def _get_enum_fields(schema_definition: Definition, definition_dict: dict):   # POPO update

        schema_defined_fields = schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS, [])   # POPO update
        schema_defined_fields_dict = {field.get(DEFINITION_FIELD_NAME): field for field in schema_defined_fields}   # POPO update
        field_names_to_traverse = set(schema_defined_fields_dict.keys()).intersection(set(definition_dict.keys()))  # POPO update

        for field_name in sorted(field_names_to_traverse):
            field_type = schema_defined_fields_dict.get(field_name).get(DEFINITION_FIELD_TYPE)  # POPO update
            field_schema_definition = context.get_definition_by_name(field_type)    # POPO update

            if field_schema_definition and not field_schema_definition.is_enum():   # POPO update
                field_content = definition_dict.get(field_name, [])   # POPO update

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
                    _get_enum_fields(field_schema_definition, field)    # POPO update
            elif field_schema_definition and field_schema_definition.is_enum():   # POPO update
                if field_type == target_enum_type.name:
                    field_dicts.append({field_name: definition_dict.get(field_name)})   # POPO update

    source_definition_root_key = source_definition.get_root_key()   # POPO update
    source_definition_fields = source_definition.get_top_level_fields()   # POPO update

    # Return the whole definition dictionary if the desired substructure is the root type.
    source_definition_schema = get_definition_schema(source_definition, context)    # POPO update

    if source_definition_schema:    # POPO update
        _get_enum_fields(source_definition_schema, source_definition_fields)    # POPO update
    else:
        logging.error(f"Failed to find a schema definition for the key {source_definition_root_key}.")  # POPO update

    return field_dicts


def strip_undefined_fields_from_definition(definition: Definition, context: LanguageContext) -> Definition:   # POPO update
    """
    Strip any fields that aren't defined in the definition's schema and returns a stripped copy of the definition.

    Args:
        definition (Definition): The definition to strip undefined fields from
        context (LanguageContext): The language context, used to navigate the structure and lookup definitions

    Returns:
        A copy of the original definition with undefined fields removed.
    """

    def _strip_fields(definition_dict: dict, dict_schema: Definition):  # POPO update
        defined_top_level_fields = dict_schema.get_top_level_fields().get(DEFINITION_FIELD_FIELDS, {})  # POPO update
        defined_top_level_fields_dict = {field.get(DEFINITION_FIELD_NAME): field for field in defined_top_level_fields}   # POPO update
        definition_dict_field_names = list(definition_dict.keys())  # POPO update

        for field_name in definition_dict_field_names:  # POPO update
            if field_name not in defined_top_level_fields_dict:
                logging.info(f"Removing undefined field {field_name} from definition: {definition.name}")   # POPO update
                del definition_dict[field_name]   # POPO update
            else:
                field_schema_type = defined_top_level_fields_dict.get(field_name).get(DEFINITION_FIELD_TYPE)    # POPO update
                is_array_field = is_array_type(field_schema_type)

                field_schema = context.get_definition_by_name(remove_list_type_indicator(field_schema_type))    # POPO update

                if field_schema and not context.is_enum_type(field_schema_type):
                    field_sub_dict = definition_dict.get(field_name, {})    # POPO update
                    field_dicts = [entry for entry in field_sub_dict] if is_array_field else [field_sub_dict]

                    for field_sub_dict in field_dicts:
                        _strip_fields(field_sub_dict, field_schema)

    if definition:  # POPO update
        stripped_definition = definition.copy()   # POPO update
        definition_schema = get_definition_schema(definition, context)  # POPO update
        definition_structure = stripped_definition.get_top_level_fields()   # POPO update
        _strip_fields(definition_structure, definition_schema)  # POPO update
        return stripped_definition  # POPO update
