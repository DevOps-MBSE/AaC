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


def print_json(architecture_files: list[str], output_directory) -> PluginExecutionResult:
    """Print or write to file the parsed_models from the parsed architecture_files values in JSON format."""

    def to_json(architecture_file: str, output_directory: str) -> str:
        file_name = os.path.splitext(architecture_file)[0]
        with validation(parse_file, architecture_file) as result:

            if output_directory == None:
                return f"File: {architecture_file}\n{json.dumps(result.model, indent=2)}\n"

            else:
                output_file_path = output_directory + file_name + '.json'
                print(output_file_path)
                outFile = open(output_file_path, "w")
                outFile.write(json.dumps(result.model, indent=2))
                outFile.close()
                return file_name + '.json file writen to directory'

    status = PluginExecutionStatusCode.SUCCESS
    messages = []
    for arch_file in architecture_files:
        with plugin_result(plugin_name, to_json, arch_file, output_directory) as result:
            messages = result.messages
            if not result.is_success():
                status = result.status_code

    return PluginExecutionResult(plugin_name, status, messages)






