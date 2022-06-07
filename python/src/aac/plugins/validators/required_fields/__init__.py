"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.required_fields._validate_required_fields import validate_required_fields

PLUGIN_YAML_FILE = "required_fields.aac"


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """
    return get_resource_file_contents(__package__, PLUGIN_YAML_FILE)


@hookimpl
def register_validators() -> ValidatorPlugin:
    """
    Returns the information about the validation plugin necessary to execute validation.

    Returns:
        A collection of data necessary to manage and execute validation plugins.
    """
    validation_definition = get_validation_definition_from_plugin_definitions(get_plugin_aac_definitions())
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_required_fields)


def get_required_fields(definition: Definition) -> list[str]:
    """Return a list of field names if the definition has a required field."""
    required_validation = [v for v in definition.get_validations() if v.get("name") == REQUIRED_FIELDS_VALIDATION_STRING]
    return required_validation and required_validation[0].get("arguments") or []


REQUIRED_FIELDS_VALIDATION_STRING = register_validators().name
