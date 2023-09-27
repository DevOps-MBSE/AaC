"""AaC Plugin implementation module for the Version plugin."""

from os import path
from typing import Callable
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, OperationCancelled, ExecutionError
from aac.context.language_context import LanguageContext

plugin_name = "Generate Plugin"


def gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool) -> ExecutionResult:
    """Print the AaC package version."""

    print(f"DEBUG: Running the AaC Gen-Plugin with:\n   aac_plugin_file: {aac_plugin_file}\n   code_output: {code_output}\n   test_output: {test_output}\n   doc_output: {doc_output}\n   no_prompt: {no_prompt}")

    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])


def after_gen_plugin_generate(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool, generate: Callable) -> ExecutionResult:
    gen_plugin_generator_file = path.abspath(path.join(__file__, "./gen_plugin_generator.aac"))
    return generate(aac_plugin_file, gen_plugin_generator_file, code_output, test_output, doc_output, no_prompt)