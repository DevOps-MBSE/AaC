"""AaC Plugin implementation module for the Version plugin."""

from os import path, mkdir
from typing import Callable
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, OperationCancelled, ExecutionError
from aac.context.language_context import LanguageContext

plugin_name = "Generate Plugin"


def gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool, force_overwrite: bool) -> ExecutionResult:
    """Print the AaC package version."""

    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])


def after_gen_plugin_generate(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool, force_overwrite: bool, generate: Callable) -> ExecutionResult:
    gen_plugin_generator_file = path.abspath(path.join(path.dirname(__file__), "./gen_plugin_generator.aac"))
    return generate(aac_plugin_file, gen_plugin_generator_file, code_output, test_output, doc_output, no_prompt, force_overwrite)

def gen_project(aac_project_file: str, output: str, no_prompt: bool, force_overwrite: bool) -> ExecutionResult:
    """Print the AaC package version."""

    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])


def after_gen_project_generate(aac_project_file: str, output: str, no_prompt: bool, force_overwrite: bool, generate: Callable) -> ExecutionResult:
    gen_plugin_generator_file = path.abspath(path.join(path.dirname(__file__), "./gen_plugin_generator.aac"))
    result =  generate(aac_project_file, gen_plugin_generator_file, output, output, output, no_prompt, force_overwrite)
    if result.is_success():
        src_path = path.join(output, "src")
        tests_path = path.join(output, "tests")
        docs_path = path.join(output, "docs")
        if not path.exists(src_path):
            mkdir(src_path)
        if not path.exists(tests_path):
            mkdir(tests_path)
        if not path.exists(docs_path):
            mkdir(docs_path)
        
    return result