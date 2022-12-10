"""Validation plugin to ensure that each model definition has subcomponents of type model."""

from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.validators._common import get_plugin_validations_from_definitions
from aac.plugins.validators.subcomponent_type._subcomponent_type import PLUGIN_NAME, validate_subcomponent_types


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(PLUGIN_NAME)
    plugin.register_definitions(_get_plugin_definitions())
    plugin.register_definition_validations(_get_plugin_validations())
    return plugin


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "subcomponent_type.yaml")


def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_subcomponent_types)
