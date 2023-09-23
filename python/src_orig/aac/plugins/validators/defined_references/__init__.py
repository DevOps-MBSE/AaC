"""Validation plugin to ensure that each validation definition has a corresponding validation implementation."""

from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.validators.defined_references._validate_references import PLUGIN_NAME, validate_references
from aac.plugins.validators._common import get_plugin_validations_from_definitions


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
    return get_plugin_definitions_from_yaml(__package__, "defined_references.yaml")


def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_references)
