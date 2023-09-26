"""AaC Plugin implementation module for the Version plugin."""

from os import path
from typing import Callable
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, OperationCancelled, ExecutionError
from aac.context.language_context import LanguageContext

plugin_name = "Generate Plugin"

def run_aftger_generate(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool, generate: Callable) -> ExecutionResult:
    gen_plugin_generator_file = path.abspath(path.join(__file__, "./gen_plugin.aac"))
    return generate(aac_plugin_file, gen_plugin_generator_file, code_output, test_output, doc_output, no_prompt)


def gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, no_prompt: bool, no_setup: bool) -> ExecutionResult:
    """Print the AaC package version."""

    print(f"DEBUG: Running the AaC Gen-Plugin with:\n   aac_plugin_file: {aac_plugin_file}\n   code_output: {code_output}\n   test_output: {test_output}\n   no_prompt: {no_prompt}\n   no_setup: {no_setup}")

    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])
