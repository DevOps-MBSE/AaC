"""A plugin to print JSON schema of AaC model files."""

import json

from aac.parser import parse_file
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    PluginExecutionStatusCode,
    plugin_result,
)
from aac.validator import validation

plugin_name = "gen-json"


def print_json(architecture_files: list[str]) -> PluginExecutionResult:
    """Print the parsed_models from the parsed architecture_files values in JSON format."""

    def to_json(architecture_file: str) -> str:
        with validation(parse_file, architecture_file) as result:
            return f"File: {architecture_file}\n{json.dumps(result.model, indent=2)}\n"

    status = PluginExecutionStatusCode.SUCCESS
    messages = []
    for arch_file in architecture_files:
        with plugin_result(plugin_name, to_json, arch_file) as result:
            messages = result.messages
            if not result.is_success():
                status = result.status_code

    return PluginExecutionResult(plugin_name, status, messages)
