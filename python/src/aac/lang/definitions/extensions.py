"""Module for handling Definitions and Extensions."""

import logging
from aac.lang.constants import (
    DEFINITION_FIELD_ADD,
    DEFINITION_FIELD_ARGUMENTS,
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_EXTENSION_SCHEMA,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_VALIDATION,
    DEFINITION_FIELD_VALUES,
)

from aac.lang.definitions.definition import Definition
from aac.lang.language_error import LanguageError


def apply_extension_to_definition(extension_definition: Definition, target_definition: Definition) -> None: ### POPO update ###
    """
    Apply the extension to the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The definition in the context to which to apply the extension.

    Raises:
        LanguageError: Raised when there is an unrecoverable internal error when applying an extension
    """
    target_definition_fields_dict = target_definition.get_top_level_fields()    ### POPO update ###
    extension_additional_content = _get_extension_additional_content_dict(extension_definition) ### POPO update ###
    extension_field_name = _get_extension_field_name(extension_definition)  ### POPO update ###

    original_field_values = target_definition_fields_dict.get(extension_field_name) ### POPO update ###
    if original_field_values is not None:
        updated_values = []

        if extension_additional_content is not None and DEFINITION_FIELD_ADD in extension_additional_content:   ### POPO update ###
            new_values = extension_additional_content.get(DEFINITION_FIELD_ADD) or []   ### POPO update ###
            if extension_definition.is_enum_extension():
                updated_values = _combine_enum_values(original_field_values, new_values)    ### POPO update ###
            else:
                updated_values = _combine_schema_fields(original_field_values, new_values)  ### POPO update ###

            target_definition_fields_dict[extension_field_name] = updated_values    ### POPO update ###
            _add_extension_required_fields_to_definition(target_definition_fields_dict, extension_additional_content)   ### POPO update ###

        else:
            missing_ext_content_message = f"Error when attempting to apply extension '{extension_definition.name}'. The extension is missing the appropriate extension content field '{target_definition.get_root_key()}Ext'"
            logging.error(missing_ext_content_message)
            raise LanguageError(missing_ext_content_message)

    else:
        extension_type = get_extension_definition_type(extension_definition)    ### POPO update ###
        incorrect_target_error_message = f"Attempted to apply the extension '{extension_definition.name}' ({extension_type}) to an incompatible target definition '{target_definition.name}' ({target_definition.get_root_key()})"  ### POPO update ###
        logging.error(incorrect_target_error_message)


def remove_extension_from_definition(extension_definition: Definition, target_definition: Definition) -> None:  ### POPO update ###
    """
    Remove the extension from the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The extension definition to apply to the context.

    Raises:
        LanguageError: Raised when there is an unrecoverable internal error when removing an extension
    """
    target_definition_fields = target_definition.get_top_level_fields() ### POPO update ###
    extension_additional_content = _get_extension_additional_content_dict(extension_definition) ### POPO update ###
    extension_field_name = _get_extension_field_name(extension_definition)  ### POPO update ###
    extension_target_field = target_definition_fields.get(extension_field_name) ### POPO update ###

    if extension_target_field:
        elements_to_remove = extension_additional_content.get(DEFINITION_FIELD_ADD) ### POPO update ###
        if not isinstance(elements_to_remove, list):
            elements_to_remove = [elements_to_remove]

        for element_to_remove in elements_to_remove:

            if extension_definition.is_schema_extension():  ### POPO update ###
                field_name_to_remove = element_to_remove.get(DEFINITION_FIELD_NAME, "") ### POPO update ###
                _remove_schema_extension_from_fields(field_name_to_remove, extension_target_field)
            elif extension_definition.is_enum_extension():  ### POPO update ###
                _remove_enum_extension_from_values(element_to_remove, extension_target_field)
            else:
                logging.error(
                    f"Unrecognized extension type found in '{extension_definition}'. Valid types are '{DEFINITION_FIELD_EXTENSION_ENUM}' and '{DEFINITION_FIELD_EXTENSION_SCHEMA}'" ### POPO update ###
                )
    else:
        missing_target_error_message = f"Attempted to remove a missing extension field from the target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'"
        logging.error(missing_target_error_message)
        raise LanguageError(missing_target_error_message)

    _remove_extension_required_fields_to_definition(target_definition_fields, extension_additional_content) ### POPO update ###


def get_extension_definition_type(definition: Definition) -> str:   ### POPO update ###
    """Returns the extension's substructure type based on whether the extension is extending an enum or schema definition."""
    return DEFINITION_FIELD_EXTENSION_ENUM if definition.is_enum_extension() else DEFINITION_FIELD_EXTENSION_SCHEMA ### POPO update ###


def _remove_schema_extension_from_fields(field_name_to_remove: str, target_definition_fields: list[dict]):  ### POPO update ###
    """Specifically remove the extension's field from the target definition's fields."""    
    matching_fields = [field for field in target_definition_fields if field.get(DEFINITION_FIELD_NAME) == field_name_to_remove] ### POPO update ###

    if len(matching_fields) == 0:
        logging.error(f"Failed to find the field '{field_name_to_remove}' in the target fields '{target_definition_fields}'")
    else:
        matching_field, *_ = matching_fields
        target_definition_fields.remove(matching_field) ### POPO update ###


def _remove_enum_extension_from_values(enum_to_remove: str, target_enum_values: list[str]):
    """Specifically remove the extension's enum value from the target definition's enum values."""
    if enum_to_remove not in target_enum_values:
        logging.error(f"Failed to find the enum value '{enum_to_remove}' in the target values '{target_enum_values}'")
    else:
        target_enum_values.remove(enum_to_remove)


def _get_extension_additional_content_dict(extension_definition: Definition) -> dict:   ### POPO update ###
    """Return the extension's additive information fields based on the extension's sub-type (enumExt/dataExt)."""
    extension_definition_fields = extension_definition.get_top_level_fields()   ### POPO update ###   ### POPO update ###
    extension_type = get_extension_definition_type(extension_definition)    ### POPO update ###
    return extension_definition_fields.get(extension_type)  ### POPO update ###


def _get_extension_field_name(extension_definition: Definition) -> str: ### POPO update ###
    """Get the appropriate field name (values/fields) for the extension's additional content."""
    return DEFINITION_FIELD_VALUES if extension_definition.is_enum_extension() else DEFINITION_FIELD_FIELDS ### POPO update ###


def _combine_enum_values(original_values: list[str], new_values: list[str]) -> list[str]:
    """Return a list of all unique original and new enum values combined together."""
    return list(set(original_values + new_values))


def _combine_schema_fields(original_fields: list[dict], new_fields: list[dict]) -> list[dict]:
    """Return a list of all unique original and new data fields combined together."""
    updated_fields_dict = {value.get(DEFINITION_FIELD_NAME): value for value in original_fields}    ### POPO update ###
    unique_new_fields = [field for field in new_fields if field.get(DEFINITION_FIELD_NAME) not in updated_fields_dict.keys()]
    new_fields_dict = {value.get(DEFINITION_FIELD_NAME): value for value in unique_new_fields}  ### POPO update ###
    updated_fields_dict.update(new_fields_dict)
    return list(updated_fields_dict.values())


def _remove_enum_values(target_values: list, values_to_remove: list) -> list:
    """Return a list of the target values sans any of the values to remove."""
    dict_of_values_to_remove = {value: value for value in values_to_remove}
    updated_values_list = {value: value for value in target_values if value not in dict_of_values_to_remove}
    return list(updated_values_list.values())


def _remove_schema_fields(target_fields: list, fields_to_remove: list):
    """Return a list of the target fields sans any of the fields to remove."""
    dict_of_fields_to_remove = {field.get(DEFINITION_FIELD_NAME): field for field in fields_to_remove}  ### POPO update ###
    updated_fields_list = {
        field.get(DEFINITION_FIELD_NAME): field ### POPO update ###
        for field in target_fields
        if field.get(DEFINITION_FIELD_NAME) not in dict_of_fields_to_remove ### POPO update ###
    }
    return list(updated_fields_list.values())


def _add_extension_required_fields_to_definition(
    target_definition_fields: dict, extension_additional_content_fields: dict   ### POPO update ###
) -> None:
    """Add any additional required fields from the extension to the target definition."""
    extension_required_fields = extension_additional_content_fields.get("required")
    definition_validations = _get_definition_validations(target_definition_fields)  ### POPO update ###

    if not definition_validations:  ### POPO update ###
        target_definition_fields[DEFINITION_FIELD_VALIDATION] = []  ### POPO update ###

    required_fields_validation = _get_required_fields_validation_for_definition(target_definition_fields)   ### POPO update ###
    if extension_required_fields:
        target_definition_fields[DEFINITION_FIELD_VALIDATION].append(required_fields_validation)    ### POPO update ###
        required_fields_validation[DEFINITION_FIELD_ARGUMENTS].extend(extension_required_fields)    ### POPO update ###


def _remove_extension_required_fields_to_definition(
    target_definition_fields: dict, extension_additional_content_fields: dict   ### POPO update ###
) -> None:
    """Remove the extension's required fields from the target definition's required fields."""
    target_required_fields = []
    definition_validations = _get_definition_validations(target_definition_fields)  ### POPO update ###
    extension_required_fields = extension_additional_content_fields.get("required") or []

    if definition_validations:  ### POPO update ###
        required_fields_validation = _get_required_fields_validation_for_definition(target_definition_fields)   ### POPO update ###
        target_required_fields = required_fields_validation.get(DEFINITION_FIELD_ARGUMENTS) ### POPO update ###

    for required_field in extension_required_fields:
        if required_field in target_required_fields:
            target_required_fields.remove(required_field)
        else:
            logging.error(
                f"Extension-applied required field '{required_field}' is not present in target dictionary: '{target_definition_fields}'"    ### POPO update ###
            )


def _get_required_fields_validation_string() -> str:
    """Return the name of the required fields validation."""
    from aac.plugins.validators.required_fields import VALIDATION_NAME

    return VALIDATION_NAME


def _get_required_fields_validation_for_definition(definition_fields: dict) -> dict:    ### POPO update ###
    """Return the required fields validation on the specified definition."""    ### POPO update ###
    definition_validations = _get_definition_validations(definition_fields) ### POPO update ###
    required_fields_validation_name = _get_required_fields_validation_string()
    required_fields_validation = [
        v for v in definition_validations if v.get(DEFINITION_FIELD_NAME) == required_fields_validation_name    ### POPO update ###
    ]
    empty_required_fields_validation = {DEFINITION_FIELD_NAME: required_fields_validation_name, DEFINITION_FIELD_ARGUMENTS: []} ### POPO update ###

    return required_fields_validation[0] if required_fields_validation else empty_required_fields_validation


def _get_definition_validations(definition_fields: dict) -> list[dict]: ### POPO update ###
    """Return the list of validation definitions for the specified definition."""
    return definition_fields.get("validation") or []    ### POPO update ###   
