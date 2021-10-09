from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "jellyfish"

hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)
