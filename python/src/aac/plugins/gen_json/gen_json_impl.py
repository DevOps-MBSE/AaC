"""A plugin to print JSON schema of AaC model files."""
import json
import os

from aac.parser import parse_file
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    PluginExecutionStatusCode,
    plugin_result,
)
from aac.validator import validation


plugin_name = "gen-json"


def print_json(architecture_files: list[str], output_directory: str = None) -> PluginExecutionResult:
    """Prints the parsed_models from the parsed architecture_files values in JSON format.

    Arguments:
        architecture_files (list[str]): filepath to the architecture file to convert to JSON.
        output_directory (str): Directory in which JSON files will be written. (optional)
    """

    def to_json(architecture_file: str, output_directory: str) -> str:
        architecture_file_path = os.path.abspath(architecture_file)
        file_name, _ = os.path.splitext(os.path.basename(architecture_file_path))

        with validation(parse_file, architecture_file_path) as result:
            formatted_json = json.dumps(result.model, indent=2)

            if output_directory:
                output_file_path = os.path.join(output_directory, f"{file_name}.json")

                with open(output_file_path, "w") as out_file:
                    out_file.write(formatted_json)

                return f"Wrote JSON to {output_file_path}."

            else:
                return f"File: {architecture_file_path}\n{formatted_json}\n"

    status = PluginExecutionStatusCode.SUCCESS
    messages = []
    for arch_file in architecture_files:
        with plugin_result(plugin_name, to_json, arch_file, output_directory) as result:
            messages = messages + result.messages
            if not result.is_success():
                status = result.status_code

    return PluginExecutionResult(plugin_name, status, messages)
