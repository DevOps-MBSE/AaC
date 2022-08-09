"""Validation plugin to ensure that each definition has a valid, defined root key."""

from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.validators.root_keys._validate_root_keys import validate_root_keys
from aac.plugins.validators._common import get_plugin_validations_from_definitions


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
    return get_plugin_definitions_from_yaml(__package__, "root_keys.yaml")

def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_root_keys)
