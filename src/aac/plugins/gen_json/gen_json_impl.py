"""A plugin to print JSON schema of AaC model files."""

import json

from aac.parser import parse_file
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    PluginExecutionStatusCode,
)
from aac.validator import validation

plugin_name = "gen-json"


def print_json(architecture_files: list[str]) -> PluginExecutionResult:
    """Print the parsed_models from the parsed architecture_files values in JSON format."""
    status = PluginExecutionStatusCode.SUCCESS
    messages = []

    for architecture_file in architecture_files:
        with validation(parse_file, architecture_file) as parsed_model:
            if not parsed_model:
                status = PluginExecutionStatusCode.VALIDATION_FAILURE
            messages.append(f"File: {architecture_file}\n{json.dumps(parsed_model)}")

    return PluginExecutionResult(plugin_name, status, messages)
