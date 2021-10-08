from jellyfish._plugin import manager


def get_plugin_manager():
    """Expose the Jellyfish Plugin Manager at the package level"""
    return manager.get_plugin_manager()
