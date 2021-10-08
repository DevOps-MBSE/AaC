from jellyfish._plugin import hookspecs, JellyfishPluginManager, PLUGIN_NAMESPACE


def get_plugin_manager():
    plugin_manager = JellyfishPluginManager(PLUGIN_NAMESPACE)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_NAMESPACE)
    # plugin_manager.register(lib)

    return plugin_manager
