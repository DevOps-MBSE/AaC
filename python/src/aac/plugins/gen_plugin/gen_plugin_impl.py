"""AaC Plugin implementation module for the Version plugin."""

from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

plugin_name = "Generate Plugin"


def gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, no_prompt: bool, no_setup: bool) -> ExecutionResult:
    """Print the AaC package version."""

    print(f"Running the AaC Gen-Plugin with:\n   aac_plugin_file: {aac_plugin_file}\n   code_output: {code_output}\n   test_output: {test_output}\n   no_prompt: {no_prompt}\n   no_setup: {no_setup}")
    
    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])
