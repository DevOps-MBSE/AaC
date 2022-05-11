"""Validation plugin that ensures that only one of the fields identified via arguments is defined."""

from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions

from aac.plugins.validators.exclusive_fields._exclusive_fields import validate_exclusive_fields

PLUGIN_YAML_FILE = "exclusive_fields.yaml"


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
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_exclusive_fields)
