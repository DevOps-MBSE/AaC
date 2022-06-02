"""Module for handling Definitions and Extensions."""

import logging

from aac.lang.definitions.definition import Definition


def apply_extension_to_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Apply the extension to the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The definition to in the context to which to apply the extension.
    """
    target_definition_fields_dict = target_definition.get_top_level_fields()
    extension_additional_content = _get_extension_additional_content_dict(extension_definition)
    extension_field_name = _get_extension_field_name(extension_definition)

    original_field_values = target_definition_fields_dict.get(extension_field_name)
    if original_field_values is not None:
        updated_values = []
        new_values = extension_additional_content.get("add") or []
        if extension_definition.is_enum_extension():
            updated_values = _combine_enum_values(original_field_values, new_values)
        else:
            updated_values = _combine_schema_fields(original_field_values, new_values)

        target_definition_fields_dict[extension_field_name] = updated_values
    else:
        logging.error(
            f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'"
        )

    _add_extension_required_fields_to_defintion(target_definition_fields_dict, extension_additional_content)


def remove_extension_from_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Remove the extension from the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The extension definition to apply to the context.
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
        logging.error(
            f"Attempted to remove a missing extension field from target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'"
        )

    _remove_extension_required_fields_to_defintion(target_definition_fields, extension_additional_content)


def _get_extension_additional_content_dict(extension_definition: Definition) -> dict:
    """Return the extension's additive information fields based on the extension's sub-type (enumExt/dataExt)."""
    extension_definition_fields = extension_definition.get_top_level_fields()
    extension_type = "enum" if extension_definition.is_enum_extension() else "schema"
    ext_type = f"{extension_type}Ext"
    return extension_definition_fields.get(ext_type)


def _get_extension_field_name(extension_definition: Definition) -> str:
    """Get the appropriate field name (values/fields) for the extension's additional content."""
    return "values" if extension_definition.is_enum_extension() else "fields"


def _combine_enum_values(original_values: list, new_values: list) -> list:
    """Return a list of all unique original and new enum values combined together."""
    updated_values = {value: value for value in original_values}
    new_values = {value: value for value in new_values}
    updated_values.update(new_values)
    return list(updated_values.values())


def _combine_schema_fields(original_fields: list, new_fields: list):
    """Return a list of all unique original and new data fields combined together."""
    updated_fields_dict = {value.get("name"): value for value in original_fields}
    unique_new_fields = list(filter(lambda field: field.get("name") not in updated_fields_dict.keys(), new_fields))
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


def _add_extension_required_fields_to_defintion(target_definition_fields: dict, extension_additional_content_fields: dict) -> None:
    """Add any additional required fields from the extension to the target definition."""
    extension_required_fields = extension_additional_content_fields.get("required")

    if extension_required_fields:
        if "required" not in target_definition_fields:
            target_definition_fields["required"] = []

        target_definition_fields["required"] += extension_required_fields


def _remove_extension_required_fields_to_defintion(target_definition_fields: dict, extension_additional_content_fields: dict) -> None:
    """Remove the extension's required fields from the target definition's required fields."""
    extension_required_fields = extension_additional_content_fields.get("required") or []
    target_required_fields = target_definition_fields.get("required") or []

    for required_field in extension_required_fields:
        if required_field in target_required_fields:
            target_required_fields.remove(required_field)
        else:
            logging.error(
                f"Extension-applied required field '{required_field}' is not present in target dictionary: '{target_definition_fields}'"
            )
