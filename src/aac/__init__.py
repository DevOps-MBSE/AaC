from os.path import abspath

from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"
PROJECT_ROOT_DIR = abspath("../../")

hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

__all__ = ("run_cli", "hookimpl", "hookspec", "PROJECT_ROOT_DIR")

# note:  must come last to avoid circular import
from aac.cli import run_cli
