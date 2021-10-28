from pluggy import PluginManager

from aac import hookspecs, genjson, genplug, PLUGIN_PROJECT_NAME


def get_plugin_manager():
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" plugins
    plugin_manager.register(genjson)
    plugin_manager.register(genplug)

    return plugin_manager