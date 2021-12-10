"""A plugin to print JSON schema of AaC model files."""
import json

from aac.parser import parse_file
from aac.validator import validation


def print_json(architecture_files: list[str]) -> None:
    """
    Prints the parsed_models from the parsed architecture_files values in JSON format.
    """

    for architecture_file in architecture_files:
        print(f"File: {architecture_file}")
        with validation(parse_file, architecture_file) as parsed_model:
            _print_parsed_model(parsed_model)


def _print_parsed_model(parsed_model: dict[str, any]) -> None:
    print(json.dumps(parsed_model))
