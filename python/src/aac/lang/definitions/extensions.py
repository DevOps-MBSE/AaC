"""Module for handling Definitions and Extensions."""

import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_error import LanguageError


def apply_extension_to_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Apply the extension to the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The definition in the context to which to apply the extension.

    Raises:
        LanguageError: Raised when there is an unrecoverable internal error when applying an extension
    """
    target_definition_fields_dict = target_definition.get_top_level_fields()
    extension_additional_content = _get_extension_additional_content_dict(extension_definition)
    extension_field_name = _get_extension_field_name(extension_definition)

    original_field_values = target_definition_fields_dict.get(extension_field_name)
    if original_field_values is not None:
        updated_values = []

        if extension_additional_content is not None and "add" in extension_additional_content:
            new_values = extension_additional_content.get("add") or []
            if extension_definition.is_enum_extension():
                updated_values = _combine_enum_values(original_field_values, new_values)
            else:
                updated_values = _combine_schema_fields(original_field_values, new_values)

            target_definition_fields_dict[extension_field_name] = updated_values
            _add_extension_required_fields_to_definition(target_definition_fields_dict, extension_additional_content)

        else:
            missing_ext_content_message = f"Error when attempting to applying extension '{extension_definition.name}'. The extension is missing the appropriate extension content field '{target_definition.get_root_key()}Ext'"
            logging.error(missing_ext_content_message)
            raise LanguageError(missing_ext_content_message)

    else:
        extension_type = "enum" if extension_definition.is_enum_extension() else "schema"
        incorrect_target_error_message = f"Attempted to apply the extension '{extension_definition.name}' ({extension_type}) to an incompatible target definition '{target_definition.name}' ({target_definition.get_root_key()})"
        logging.error(incorrect_target_error_message)


def remove_extension_from_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Remove the extension from the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The extension definition to apply to the context.

    Raises:
        LanguageError: Raised when there is an unrecoverable internal error when removing an extension
    """
    target_definition_fields = target_definition.get_top_level_fields()
    extension_additional_content = _get_extension_additional_content_dict(extension_definition)
    extension_field_name = _get_extension_field_name(extension_definition)

    if target_definition_fields.get(extension_field_name):
        elements_to_remove = extension_additional_content.get("add")
        if not isinstance(elements_to_remove, list):
            elements_to_remove = [elements_to_remove]

        for element_to_remove in elements_to_remove:
            target_definition_fields[extension_field_name].remove(element_to_remove)
    else:
        missing_target_error_message = f"Attempted to remove a missing extension field from the target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'"
        logging.error(missing_target_error_message)
        raise LanguageError(missing_target_error_message)

    _remove_extension_required_fields_to_definition(target_definition_fields, extension_additional_content)


def _get_extension_additional_content_dict(extension_definition: Definition) -> dict:
    """Return the extension's additive information fields based on the extension's sub-type (enumExt/dataExt)."""
    extension_definition_fields = extension_definition.get_top_level_fields()
    extension_type = "enum" if extension_definition.is_enum_extension() else "schema"
    ext_type = f"{extension_type}Ext"
    return extension_definition_fields.get(ext_type)


def _get_extension_field_name(extension_definition: Definition) -> str:
    """Get the appropriate field name (values/fields) for the extension's additional content."""
    return "values" if extension_definition.is_enum_extension() else "fields"


def _combine_enum_values(original_values: list[str], new_values: list[str]) -> list[str]:
    """Return a list of all unique original and new enum values combined together."""
    return list(set(original_values + new_values))


def _combine_schema_fields(original_fields: list[dict], new_fields: list[dict]) -> list[dict]:
    """Return a list of all unique original and new data fields combined together."""
    updated_fields_dict = {value.get("name"): value for value in original_fields}
    unique_new_fields = [field for field in new_fields if field.get("name") not in updated_fields_dict.keys()]
    new_fields_dict = {value.get("name"): value for value in unique_new_fields}
    updated_fields_dict.update(new_fields_dict)
    return list(updated_fields_dict.values())


def _remove_enum_values(target_values: list, values_to_remove: list) -> list:
    """Return a list of the target values sans any of the values to remove."""
    dict_of_values_to_remove = {value: value for value in values_to_remove}
    updated_values_list = {value: value for value in target_values if value not in dict_of_values_to_remove}
    return list(updated_values_list.values())


def _remove_schema_fields(target_fields: list, fields_to_remove: list):
    """Return a list of the target fields sans any of the fields to remove."""
    dict_of_fields_to_remove = {field.get("name"): field for field in fields_to_remove}
    updated_fields_list = {field.get("name"): field for field in target_fields if field.get("name") not in dict_of_fields_to_remove}
    return list(updated_fields_list.values())


def _add_extension_required_fields_to_definition(target_definition_fields: dict, extension_additional_content_fields: dict) -> None:
    """Add any additional required fields from the extension to the target definition."""
    extension_required_fields = extension_additional_content_fields.get("required")
    definition_validations = _get_definition_validations(target_definition_fields)

    if not definition_validations:
        target_definition_fields["validation"] = []

    required_fields_validation = _get_required_fields_validation_for_definition(target_definition_fields)
    if extension_required_fields:
        target_definition_fields["validation"].append(required_fields_validation)
        required_fields_validation["arguments"].extend(extension_required_fields)


def _remove_extension_required_fields_to_definition(target_definition_fields: dict, extension_additional_content_fields: dict) -> None:
    """Remove the extension's required fields from the target definition's required fields."""
    target_required_fields = []
    definition_validations = _get_definition_validations(target_definition_fields)
    extension_required_fields = extension_additional_content_fields.get("required") or []

    if definition_validations:
        required_fields_validation = _get_required_fields_validation_for_definition(target_definition_fields)
        target_required_fields = required_fields_validation.get("arguments")

    for required_field in extension_required_fields:
        if required_field in target_required_fields:
            target_required_fields.remove(required_field)
        else:
            logging.error(
                f"Extension-applied required field '{required_field}' is not present in target dictionary: '{target_definition_fields}'"
            )


def _get_required_fields_validation_string() -> str:
    """Return the name of the required fields validation."""
    from aac.plugins.validators.required_fields import PLUGIN_NAME
    return PLUGIN_NAME


def _get_required_fields_validation_for_definition(definition_fields: dict) -> dict:
    """Return the required fields validation on the specified definition."""
    definition_validations = _get_definition_validations(definition_fields)
    required_fields_validation_name = _get_required_fields_validation_string()
    required_fields_validation = [v for v in definition_validations if v.get("name") == required_fields_validation_name]
    empty_required_fields_validation = {"name": required_fields_validation_name, "arguments": []}

    return required_fields_validation[0] if required_fields_validation else empty_required_fields_validation


def _get_definition_validations(definition_fields: dict) -> list[dict]:
    """Return the list of validation definitions for the specified definition."""
    return definition_fields.get("validation") or []
