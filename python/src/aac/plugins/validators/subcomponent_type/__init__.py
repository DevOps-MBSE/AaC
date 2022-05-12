"""Validation plugin to ensure that each model definition has subcomponents of type model."""

from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.subcomponent_type._subcomponent_type import validate_subcomponent_types

PLUGIN_YAML_FILE = "subcomponent_type.yaml"


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
    Return information about the validation plugin necessary to execute validation.

    Returns:
        A collection of data necessary to manage and execute validation plugins.
    """
    validation_definition = get_validation_definition_from_plugin_definitions(get_plugin_aac_definitions())
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_subcomponent_types)
