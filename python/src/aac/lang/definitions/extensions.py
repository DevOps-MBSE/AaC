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
    target_definition_fields = target_definition.get_top_level_fields()
    extension_additional_content = _get_extension_additional_content_dict(extension_definition)
    extension_field_name = _get_extension_field_name(extension_definition)

    if target_definition_fields.get(extension_field_name):
        target_definition_fields[extension_field_name] += extension_additional_content.get("add")
    else:
        logging.error(
            f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'"
        )

    _add_extension_required_fields_to_defintion(target_definition_fields, extension_additional_content)


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
