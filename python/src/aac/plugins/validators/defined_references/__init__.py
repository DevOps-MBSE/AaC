"""Validation plugin to ensure that each validation definition has a corresponding validation implementation."""

from aac.io.parser import parse
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.defined_references._validate_references import validate_references


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_definitions(_get_plugin_definitions())
    plugin.register_validations(_get_plugin_validations())
    return plugin


def _get_plugin_definitions():
    plugin_resource_file_args = (__package__, "defined_references.yaml")
    plugin_definitions = parse(
        get_resource_file_contents(*plugin_resource_file_args),
        get_resource_file_path(*plugin_resource_file_args),
    )
    return plugin_definitions


def _get_plugin_validations():
    validation_definition = get_validation_definition_from_plugin_definitions(_get_plugin_definitions())
    return [
        ValidatorPlugin(validation_definition.name, validation_definition, validate_references)
    ]
