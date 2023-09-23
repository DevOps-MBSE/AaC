"""Provides command line processing for the aac tool."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.cli.aac_execution_result import ExecutionResult, ExecutionStatus, ExecutionError, OperationCancelled
from pluggy import HookimplMarker, HookspecMarker

PLUGIN_PROJECT_NAME = "aac"
hookimpl = HookimplMarker(PLUGIN_PROJECT_NAME)
hookspec = HookspecMarker(PLUGIN_PROJECT_NAME)

__all__ = (
    "AacCommand",
    "AacCommandArgument",
    hookimpl,
    hookspec,
    "ExecutionResult",
    "ExecutionStatus",
    "ExecutionError",
    "OperationCancelled",
    "get_plugin",
)
