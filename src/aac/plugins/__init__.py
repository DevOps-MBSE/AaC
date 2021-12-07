"""Provides plugin management functions and access to the default plugins for the AaC project."""
from pluggy import PluginManager, HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = __package__
hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

from aac.plugins import plugin_manager


def get_plugin_manager() -> PluginManager:
    """
    Gets the plugin manager and automatically registers internal plugins.

    Returns:
        The plugin manager.
    """
    return plugin_manager.get_plugin_manager()


def get_plugin_model_definitions():
    """
    Gets all a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of plugin defined models.
    """
    return plugin_manager.get_plugin_model_definitions()
