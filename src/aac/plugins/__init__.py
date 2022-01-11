"""Provides plugin management functions and access to the default plugins for the AaC project."""

from attr import attrs, attrib, validators
from pluggy import PluginManager, HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"
hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

from aac.plugins import plugin_manager


@attrs(slots=True)
class PluginError(Exception):
    """A base class representing a plugin error condition."""

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class OperationCancelled(Exception):
    """A base class representing an cancelled plugin operation condition."""

    message: str = attrib(validator=validators.instance_of(str))


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager and automatically register internal plugins.

    Returns:
        The plugin manager.
    """
    return plugin_manager.get_plugin_manager()


def get_plugin_model_definitions():
    """
    Get a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of plugin defined models.
    """
    return plugin_manager.get_plugin_model_definitions()
