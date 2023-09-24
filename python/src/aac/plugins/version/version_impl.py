"""AaC Plugin implementation module for the Version plugin."""

from aac import __version__
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

plugin_name = "Version"


def version() -> ExecutionResult:
    """Print the AaC package version."""
    
    return ExecutionResult(plugin_name, "version", ExecutionStatus.SUCCESS, [__version__])
