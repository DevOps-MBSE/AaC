"""AaC Plugin implementation module for the Validate plugin."""


import logging

from os import linesep
from typing import Optional

from aac.io.parser import parse, ParserError
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validate import validated_source, validated_definition

plugin_name = "Validate"


def validate(architecture_file: str, definition_name: Optional[str] = None) -> PluginExecutionResult:
    """
    Validate the AaC definition file.

    Args:
        architecture_file (str): The path to the AaC file to be validated.
        definition_name (Optional[str]): The name of the definition in the file to validate.
    """

    def _validate() -> str:
        if definition_name:
            return _validate_definition_in_file(architecture_file, definition_name)
        else:
            return _validate_context_and_file(architecture_file)

    with plugin_result(plugin_name, _validate) as result:
        return result


def _validate_definition_in_file(file_path, definition_name) -> str:
    success_message = f"'{definition_name}' in {file_path} is valid."

    try:
        definitions_in_file = parse(file_path)
    except ParserError as error:
        raise ParserError(error.source, error.errors) from None
    else:
        definition_to_validate = get_definition_by_name(definition_name, definitions_in_file)
        if definition_to_validate:
            with validated_definition(definition_to_validate) as result:
                return _get_validation_success_message(success_message, result)
        else:
            active_context = get_active_context()
            target_definition = active_context.get_definition_by_name(definition_name)

            possible_source_message = ""
            if target_definition:
                possible_source_message = f"Definition '{definition_name}' can be found in '{target_definition.source.uri}'"

            possible_definitions_in_file = [definition.name for definition in definitions_in_file]

            missing_definition_error_message = linesep.join(
                [
                    f"'{definition_name}' was not found in the file.",
                    f"Definitions available in '{file_path}' are {possible_definitions_in_file}",
                    possible_source_message
                ]
            )
            logging.error(missing_definition_error_message)
            raise PluginError(missing_definition_error_message)


def _validate_context_and_file(file_path) -> str:
    success_message = f"{file_path} is valid."
    with validated_source(file_path) as result:
        return _get_validation_success_message(success_message, result)


def _get_validation_success_message(default_message, validation_result) -> str:
    plugin_messages = validation_result.get_messages_as_string()
    return_message = f"{default_message}{linesep}{plugin_messages}"
    return return_message
