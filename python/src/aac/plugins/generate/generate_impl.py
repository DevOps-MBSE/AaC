"""AaC Plugin implementation module for the Version plugin."""

from os import path
from typing import Callable
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, OperationCancelled, ExecutionError
from aac.context.language_context import LanguageContext

plugin_name = "Generate Plugin"


def gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, no_prompt: bool, no_setup: bool) -> ExecutionResult:
    """Print the AaC package version."""

    print(f"DEBUG: Running the AaC Gen-Plugin with:\n   aac_plugin_file: {aac_plugin_file}\n   code_output: {code_output}\n   test_output: {test_output}\n   no_prompt: {no_prompt}\n   no_setup: {no_setup}")

    # setup directories
    code_out_dir, test_out_dir = get_output_directories(aac_plugin_file, code_output, test_output, no_prompt)

    print(f"DEBUG: code_out_dir: {code_out_dir} test_out_dir: {test_out_dir}")

    # build out properties
    # the templates need data from the plugin model to generate code
    code_gen_props = {}
    context = LanguageContext()
    parsed_definitions = context.parse_and_load(aac_plugin_file)
    plugin_definitions = [definition for definition in parsed_definitions if definition.get_root_key == "plugin"]
    if not plugin_definitions:
        return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.GENERAL_FAILURE, [f"Could not load plugin definition from {aac_plugin_file}"])
    if len(plugin_definitions) == 0:
        return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.GENERAL_FAILURE, [f"Could not load plugin definition from {aac_plugin_file}"])
    if len(plugin_definitions) > 1:
        return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.GENERAL_FAILURE, [f"Found multiple plugin definitions in {aac_plugin_file}"])
    the_plugin_definition = plugin_definitions[0]
    
    code_gen_props["plugin"] = the_plugin_definition.structure["plugin"]
        
    # build out jinja2 utility functions
    def get_python_name(name: str) -> str:
        return name.replace(" ", "_").replace("-", "_").lower()
    
    func_dict: dict[str, Callable] = {
        "get_python_name": get_python_name
    }
    
    # TODO: figure out how to load func_dict into the jinja2 environment

    # TODO: generate code
    
    # TODO: write output to files
    
    return ExecutionResult(plugin_name, "gen-plugin", ExecutionStatus.SUCCESS, [])

def get_output_directories(aac_plugin_file: str, code_output: str, test_output: str, no_prompt: bool) -> tuple[str, str]:

    code_out: str = "."
    test_out: str = "."
    
    if not code_output or len(code_output) == 0:
        aac_plugin_path = path.abspath(aac_plugin_file)
        if not path.exists(aac_plugin_file):
            raise ExecutionError(f"The provided AaC Plugin file does not exist: {aac_plugin_file}")
        code_out = path.dirname(aac_plugin_path)
    if not test_output or len(test_output) == 0:
        test_out = code_out.replace("src", "tests")

    if not no_prompt:
        print("AaC Gen-Plugin will generate code and tests in the following directories:")
        print(f"   code: {code_out}")
        print(f"   tests: {test_out}")
        approval = "first"
        while approval not in ["y", "Y", "yes", "Yes", "YES", "n", "N", "no", "No", "NO"]:
            approval = input("Do you want to continue? (y/n): ")
        if approval in ["y", "Y", "yes", "Yes", "YES"]:
            return (code_out, test_out)
        else:
            raise OperationCancelled("User cancelled operation.")

    return (code_out, test_out)
