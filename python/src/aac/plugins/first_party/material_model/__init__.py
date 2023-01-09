"""The material-model plugin module."""

from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.first_party.material_model.material_model_impl import plugin_name


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_definitions(_get_plugin_definitions())
    return plugin


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "material_model.yaml")
