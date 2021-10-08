from jellyfish import hookspecs, PLUGIN_PROJECT_NAME
from pluggy import PluginManager


def get_plugin_manager():
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    return plugin_manager
