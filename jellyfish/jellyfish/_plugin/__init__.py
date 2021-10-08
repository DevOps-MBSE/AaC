from pluggy import HookimplMarker, HookspecMarker, PluginManager

PLUGIN_NAMESPACE = "jellyfish"

hookimpl = HookimplMarker(PLUGIN_NAMESPACE)
hookspec = HookspecMarker(PLUGIN_NAMESPACE)


class JellyfishPluginManager(PluginManager):
    """ """

    def __init__(self, name) -> None:
        self.name = name
        super().__init__(name)
        self.register(self)
