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

       (optional) if output directory is given to the cli, parsed_models with be writen to
        a new file in user defined directory

    """

    def to_json(architecture_file: str, output_directory: str) -> str:
        file_name = os.path.basename(architecture_file)
        file_ext = os.path.splitext(file_name)[1]

        with validation(parse_file, architecture_file) as result:

            if output_directory is None:
                return f"File: {architecture_file}\n{json.dumps(result.model, indent=2)}\n"

            else:
                if file_ext == '':
                    file_name = (file_name + '.json')
                else:
                    file_name = file_name.replace(file_ext, '.json')

                output_file_path = os.path.join(output_directory, file_name)
                outFile = open(output_file_path, "w")
                outFile.write(json.dumps(result.model, indent=2))
                outFile.close()
                return f"Successfully added {file_name} to directory"

    status = PluginExecutionStatusCode.SUCCESS
    messages = []
    for arch_file in architecture_files:
        with plugin_result(plugin_name, to_json, arch_file, output_directory) as result:
            messages = result.messages
            if not result.is_success():
                status = result.status_code

    return PluginExecutionResult(plugin_name, status, messages)






