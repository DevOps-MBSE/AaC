from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"

hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

__all__ = ("run_CLI", "hookimpl", "hookspec")

# note:  must come last to avoid circular import
from aac.cli import run_CLI
