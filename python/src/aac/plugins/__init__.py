"""Provides plugin management functions and access to the default plugins for the AaC project."""

from attr import attrs, attrib, validators
from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"
hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)


@attrs(slots=True)
class PluginError(Exception):
    """A base class representing a plugin error condition."""

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class OperationCancelled(Exception):
    """A base class representing an cancelled plugin operation condition."""

    message: str = attrib(validator=validators.instance_of(str))
