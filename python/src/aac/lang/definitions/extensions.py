"""Module for dealign with Definitions and Extensions."""

import logging

from aac.lang.definitions.definition import Definition


def apply_extension_to_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Apply the extension to the definition it it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The extension definition to apply to the context.
    """
    extension_type = "enum" if extension_definition.is_enum_extension() else "data"
    extension_field_name = "values" if extension_definition.is_enum_extension() else "fields"

    ext_type = f"{extension_type}Ext"
    target_definition_extension_sub_dict = target_definition.get_fields()
    extension_definition_fields = extension_definition.get_fields()

    extension_subtype_sub_dict = extension_definition_fields.get(ext_type)
    if target_definition_extension_sub_dict.get(extension_field_name):
        target_definition_extension_sub_dict[extension_field_name] += extension_subtype_sub_dict.get("add")
    else:
        logging.error(f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'")

    _add_extension_required_fields_to_defintion(target_definition_extension_sub_dict, extension_subtype_sub_dict)


def remove_extension_from_definition(extension_definition: Definition, target_definition: Definition) -> None:
    """
    Remove the extension from the definition it modifies.

    Args:
        extension_definition (Definition): The extension definition to apply to the context.
        target_definition (Definition): The extension definition to apply to the context.
    """
    extension_type = "enum" if extension_definition.is_enum_extension() else "data"
    extension_field_name = "values" if extension_definition.is_enum_extension() else "fields"

    ext_type = f"{extension_type}Ext"
    target_definition_extension_sub_dict = target_definition.get_fields()
    extension_definition_fields = extension_definition.get_fields()

    extension_subtype_sub_dict = extension_definition_fields.get(ext_type)
    if target_definition_extension_sub_dict.get(extension_field_name):
        target_definition_extension_sub_dict[extension_field_name].remove(extension_subtype_sub_dict.get("add"))
    else:
        logging.error(f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}' target definition '{target_definition.name}'")

    _remove_extension_required_fields_to_defintion(target_definition_extension_sub_dict, extension_subtype_sub_dict)


def _add_extension_required_fields_to_defintion(target_definition_sub_dict, extension_dictionary_sub_dict):
    if "required" in extension_dictionary_sub_dict:

        if "required" not in target_definition_sub_dict:
            target_definition_sub_dict["required"] = []

        target_definition_sub_dict["required"] += extension_dictionary_sub_dict.get("required") or []


def _remove_extension_required_fields_to_defintion(target_definition_sub_dict, extension_dictionary_sub_dict):
    if "required" in extension_dictionary_sub_dict:

        if "required" not in target_definition_sub_dict:
            target_definition_sub_dict["required"] = []

        target_definition_sub_dict["required"] += extension_dictionary_sub_dict.get("required") or []
