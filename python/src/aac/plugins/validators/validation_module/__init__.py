"""Validation plugin to ensure that each validation definition has a corresponding validation function."""

from aac.package_resources import get_resource_file_contents
from aac import parser
from aac.plugins import hookimpl
from aac.plugins.validators import get_validation_definition_from_plugin_definitions
from aac.validation.Validator_Plugin import Validator_Plugin

PLUGIN_YAML_FILE = "validation_module.yaml"


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Returns the CommandBehaviorType modeling language extension to the plugin infrastructure.

    Returns:
        string representing yaml extensions and data definitions employed by the plugin
    """
    return get_resource_file_contents(__package__, PLUGIN_YAML_FILE)


@hookimpl
def register_validators() -> Validator_Plugin:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """
    validation_definition = get_validation_definition_from_plugin_definitions(__name__, get_plugin_aac_definitions())
    return Validator_Plugin.from_definition(validation_definition)
