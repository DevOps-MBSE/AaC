"""The AaC Root schema must have name plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)
from aac.context.language_error import LanguageError
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from typing import Any


plugin_name = "Root schema must have name"


def _get_fields(schema) -> list[str]:
    """Returns a list of the fields in the parent schema."""
    context: LanguageContext = LanguageContext()
    fields: list[str] = []
    for field in schema.fields:
        fields.append(field.name)
    if schema.extends:
        for ext in schema.extends:
            parent_schema = context.get_definitions_by_name(ext.name)
            if len(parent_schema) == 1:
                fields.extend(_get_fields(parent_schema[0].instance))
            elif len(parent_schema) > 1:
                raise LanguageError(
                    f"Unable to identify unique definition for {ext.name}:  found {parent_schema} ", "Unknown location"
                )
    return fields


def root_schema_has_name(
    instance: Any, definition: Definition, defining_schema
) -> ExecutionResult:
    """Business logic for the Root schema has name constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    context = LanguageContext()
    if context.is_aac_instance(instance, "aac.lang.Schema"):
        if instance.root:
            # we have one special case for 'import' which is a root without a name, so allow that
            if instance.root == "import":
                return ExecutionResult(
                    plugin_name, "Root schema has name", status, messages
                )

            # get the list of fields in the instance as well as the fields in the parent schema
            fields = _get_fields(instance)  # Could we get the location of the instance and pass it to the function?
            if "name" not in fields:
                status = ExecutionStatus.GENERAL_FAILURE
                error_msg = ExecutionMessage(
                    f"Root schema {instance.name} must have a field named 'name'",
                    MessageLevel.ERROR,
                    "No file to reference" if not definition.source else definition.source.uri,
                    None,
                )
                messages.append(error_msg)

    return ExecutionResult(plugin_name, "Root schema has name", status, messages)
