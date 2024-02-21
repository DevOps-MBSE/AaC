"""__init__.py module for the Constraint Assignment Arguments plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from os.path import join, dirname
from typing import Any
from aac.execute.aac_execution_result import (
    ExecutionResult,
)
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.execute.plugin_runner import PluginRunner


from aac.plugins.constraint_assignment_arguments.constraint_assignment_arguments_impl import (
    plugin_name,
)


from aac.plugins.constraint_assignment_arguments.constraint_assignment_arguments_impl import (
    check_arguments_against_constraint_definition,
)


constraint_assignment_arguments_aac_file_name = "constraint_assignment_arguments.aac"


def run_check_arguments_against_constraint_definition(
    instance: Any, definition: Definition, defining_schema, arguments: Any
) -> ExecutionResult:
    """Ensures the arguments provided in the assignment match the arguments defined in the constraint definition."""

    return check_arguments_against_constraint_definition(
        instance, definition, defining_schema
    )


@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """

    active_context = LanguageContext()
    constraint_assignment_arguments_aac_file = join(
        dirname(__file__), constraint_assignment_arguments_aac_file_name
    )
    definitions = active_context.parse_and_load(
        constraint_assignment_arguments_aac_file
    )

    constraint_assignment_arguments_plugin_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = constraint_assignment_arguments_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(
        plugin_definition=constraint_assignment_arguments_plugin_definition
    )

    plugin_runner.add_constraint_callback(
        "Check arguments against constraint definition",
        run_check_arguments_against_constraint_definition,
    )

    active_context.register_plugin_runner(plugin_runner)
