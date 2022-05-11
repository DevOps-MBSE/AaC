"""Validation plugin to ensure that each validation definition has a corresponding validation implementation."""

from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.validators import get_validation_definition_from_plugin_definitions
from aac.plugins.validators import ValidatorPlugin
from aac.plugins.validators.validator_implementation._validator_implementation import validate_validator_implementations

PLUGIN_YAML_FILE = "validator_implementation.yaml"


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
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_validator_implementations)
