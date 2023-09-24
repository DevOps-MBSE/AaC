"""AaC Plugin implementation module for the Version plugin."""

from aac import __version__
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

plugin_name = "Generate Plugin"


def gen_plugin(aac_file: str) -> ExecutionResult:
    """Print the AaC package version."""

    print(f"Running the AaC Gen-Plugin with aac_file: {aac_file}")
    
    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])
