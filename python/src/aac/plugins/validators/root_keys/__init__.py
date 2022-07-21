"""Validation plugin to ensure that each definition has a valid, defined root key."""

from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.parser import parse
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.root_keys._validate_root_keys import validate_root_keys


PLUGIN_YAML_FILE = "root_keys.yaml"
plugin_resource_file_args = (__package__, PLUGIN_YAML_FILE)


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
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_root_keys)


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns the information about plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin_definitions = parse(
        get_plugin_aac_definitions(),
        get_resource_file_path(*plugin_resource_file_args)
    )

    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_definitions(set(plugin_definitions))
    plugin.register_validations({register_validators()})

    return plugin
