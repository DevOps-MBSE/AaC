"""Provides plugin management functions and access to the default plugins for the AaC project."""
from pluggy import PluginManager

from aac import hookspecs, genjson, genplug, parser, PLUGIN_PROJECT_NAME


def get_plugin_manager() -> PluginManager:
    """
    Gets the plugin manager and automatically registers internal plugins.

    Returns:
        The plugin manager.
    """
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" plugins
    plugin_manager.register(genjson)
    plugin_manager.register(genplug)

    return plugin_manager


def get_plugin_model_definitions():
    """
    Gets all a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of plugin defined models.
    """
    plugin_manager = get_plugin_manager()
    plugin_models_yaml = plugin_manager.hook.get_base_model_extensions()
    plugin_extensions = {}
    for plugin_ext in plugin_models_yaml:
        if len(plugin_ext) > 0:
            models = parser.parse_str(plugin_ext, "Plugin Manager Addition", False)
            plugin_extensions = models | plugin_extensions

    return plugin_extensions
