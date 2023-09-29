"""AaC Plugin implementation module for the Version2 plugin."""

from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus
from aac import __version__

plugin_name = "Version2"


def version2() -> ExecutionResult:
    """Print the AaC package version."""
    
    # TODO: implement plugin logic here
    message: str = "The version2 for the Version2 plugin has not been implemented yet."

    print(f"Version2 plugin version: {get_version()}")

    return ExecutionResult(plugin_name, "version2", ExecutionStatus.SUCCESS, [message])

def get_version() -> str:
    """Return the AaC package version."""
    # One more change
    return __version__
