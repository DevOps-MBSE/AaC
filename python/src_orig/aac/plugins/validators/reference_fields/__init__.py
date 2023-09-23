"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.validators._common import get_plugin_validations_from_definitions
from aac.plugins.validators.reference_fields._validate_reference_fields import PLUGIN_NAME, validate_reference_fields


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
    return get_plugin_definitions_from_yaml(__package__, "reference_fields.yaml")


def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_reference_fields)
