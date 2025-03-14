"""The AaC Unique Root Keys plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)
from aac.context.language_context import LanguageContext

plugin_name = "Unique Root Keys"


def root_key_names_are_unique(context: LanguageContext) -> ExecutionResult:
    """Business logic for the Root key names are unique constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    root_keys = []
    for definition in context.get_definitions():
        if definition.get_root_key() == "schema":
            if definition.instance.root:
                if definition.instance.root not in root_keys:
                    root_keys.append(definition.instance.root)
                else:
                    status = ExecutionStatus.CONSTRAINT_FAILURE
                    error_msg = ExecutionMessage(
                        f"Root key {definition.instance.root} is not unique.",
                        MessageLevel.ERROR,
                        definition.source.uri,
                        None,
                    )
                    messages.append(error_msg)

    return ExecutionResult(plugin_name, "Root key names are unique", status, messages)
