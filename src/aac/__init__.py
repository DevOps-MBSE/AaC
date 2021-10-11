from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"

hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

__all__ = ("runCLI", "hookimpl", "hookspec")

# note:  must come last to avoid circular import
from aac.cli import runCLI
