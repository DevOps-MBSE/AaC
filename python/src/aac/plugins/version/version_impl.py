"""AaC Plugin implementation module for the Version plugin."""

from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus
from aac import __version__

plugin_name = "Version"


def version() -> ExecutionResult:
    """Print the AaC package version."""
    
    message: str = __version__

    return ExecutionResult(plugin_name, "version", ExecutionStatus.SUCCESS, [message])
