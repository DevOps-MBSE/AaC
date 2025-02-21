"""The AaC Constraint Assignment Arguments plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from typing import Any


plugin_name = "Constraint Assignment Arguments"


def _process_constraint_arguments(instance: Any, constraint_args: Any, definition: Definition, context: LanguageContext) -> ExecutionResult:
    """
        Process the constraint arguments.

    Args:
        instance: The constraint we are processing
        constraint_args: Arguments for this constraint
        definition: The schema constraint
        context: The context in use

    Returns:
        ExecutionResult: An ExecutionResult with an ExecutionMessage error message if there was a problem.
    """

    if instance.arguments is None:
        constraint_args = {}
    elif not isinstance(instance.arguments, list):
        error_msg = ExecutionMessage(
            f"The Check arguments against constraint definition constraint for {instance.name} failed because the assigned arguments were not parsed as a list of entries and cannot be evaluated.  Received {instance.arguments}",
            MessageLevel.ERROR,
            definition.source.uri,
            None,
        )
        return ExecutionResult(
            plugin_name,
            "Check arguments against constraint definition",
            ExecutionStatus.GENERAL_FAILURE,
            [error_msg],
        )
    else:
        for arg in instance.arguments:
            if not isinstance(arg, dict):
                error_msg = ExecutionMessage(
                    f"The Check arguments against constraint definition constraint for {instance.name} failed because the assigned arguments were not parsed as a list of PluginInputValue entries and cannot be evaluated.  Received {instance.arguments}",
                    MessageLevel.ERROR,
                    definition.source.uri,
                    None,
                )
                return ExecutionResult(
                    plugin_name,
                    "Check arguments against constraint definition",
                    ExecutionStatus.GENERAL_FAILURE,
                    [error_msg],
                )
            constraint_args[arg["name"]] = arg["value"]
    return None


def _find_constraint_definition(context: LanguageContext, constraint_name: str) -> list:  # From check_aac_impl.py
    """
    Determines the appropriate schema or primitive constraint based on the name

    Args:
        context (LanguageContext): The context in use
        constraint_name (str): The constraint name for which we are searching

    Returns:
        list: A list size 0 (empty because match not found) or 1 (the matched schema or primitive constraint).
    """
    constraint_definition = []
    for plugin in context.get_definitions_by_root("plugin"):
        for schema_constraint in plugin.instance.schema_constraints:
            if schema_constraint.name == constraint_name:
                constraint_definition = schema_constraint
                break
        for primitive_constraint in plugin.instance.primitive_constraints:
            if primitive_constraint.name == constraint_name:
                constraint_definition = primitive_constraint
                break
    return constraint_definition


def check_arguments_against_constraint_definition(
    instance: Any, definition: Definition, defining_schema
) -> ExecutionResult:
    """
    Business logic for the Check arguments against constraint definition constraint.

    Args:
        instance (Any): The SchemaConstraintAssignment or PrimitiveConstraintAssignment we are processing
        definition (Definition): The schema constraint definition
        defining_schema: NOT USED

    Returns:
        ExecutionResult: An ExecutionResult with an ExecutionMessage error message if there was a problem.
    """

    context = LanguageContext()
    if not context.is_aac_instance(
        instance, "aac.lang.SchemaConstraintAssignment"
    ) and not context.is_aac_instance(
        instance, "aac.lang.PrimitiveConstraintAssignment"
    ):
        # the constraint failed
        error_msg = ExecutionMessage(
            f"The Check arguments against constraint definition constraint for {instance.name} failed.  You may only use this constraint on SchemaConstraintAssignment or PrimitiveConstraintAssignment definitions.  Received {type(instance)}.)",
            MessageLevel.ERROR,
            (definition.source.uri),
            None,
        )
        return ExecutionResult(
            plugin_name,
            "Check arguments against constraint definition",
            ExecutionStatus.GENERAL_FAILURE,
            [error_msg],
        )

    constraint_name = instance.name
    constraint_args: dict = {}

    exec_result = _process_constraint_arguments(instance, constraint_args, definition, context)
    if (exec_result is not None):
        return exec_result  # This is the ExecutionResult from _process_constraint_arguments so send it we have one

    constraint_definition = None
    constraint_definition = _find_constraint_definition(context, constraint_name)

    # Make sure we found the constraint definition
    if constraint_definition is None:
        # the constraint failed
        error_msg = ExecutionMessage(
            f"The Check arguments against constraint definition constraint for {instance.name} failed because the constraint definition could not be found.",
            MessageLevel.ERROR,
            definition.source.uri,
            None,
        )
        return ExecutionResult(
            plugin_name,
            "Check arguments against constraint definition",
            ExecutionStatus.GENERAL_FAILURE,
            [error_msg],
        )

    # Make sure there are no arguments if the constraint definition has no arguments
    if (
        constraint_definition.arguments is None
        or len(constraint_definition.arguments) == 0
    ):
        if constraint_args is not None and constraint_args != {}:
            # the constraint failed
            error_msg = ExecutionMessage(
                f"The Check arguments against constraint definition constraint for {instance.name} failed because the constraint definition does not have arguments, but the constraint assignment does.  Assigned arguments are {constraint_args}.",
                MessageLevel.ERROR,
                definition.source.uri,
                None,
            )
            return ExecutionResult(
                plugin_name,
                "Check arguments against constraint definition",
                ExecutionStatus.GENERAL_FAILURE,
                [error_msg],
            )

    else:  # If there are arguments, then make sure they match the constraint definition
        defined_argument_names = []
        for field in constraint_definition.arguments:
            # make sure required arguments are present
            defined_argument_names.append(field.name)
            if field.is_required and (
                not constraint_args or field.name not in constraint_args
            ):
                # the constraint failed
                error_msg = ExecutionMessage(
                    f"The Check arguments against constraint definition constraint for {instance.name} failed because the constraint definition has a required argument named {field.name} that was not found in the constraint assignment.",
                    MessageLevel.ERROR,
                    definition.source.uri,
                    None,
                )
                return ExecutionResult(
                    plugin_name,
                    "Check arguments against constraint definition",
                    ExecutionStatus.GENERAL_FAILURE,
                    [error_msg],
                )

        # make sure the arguments provided are defined in the constraint definition
        for arg_name in constraint_args:
            if arg_name not in defined_argument_names:
                # the constraint failed
                error_msg = ExecutionMessage(
                    f"The Check arguments against constraint definition constraint for {instance.name} failed because the constraint definition does not have an argument named {arg_name}, but the constraint assignment does.  Argument {arg_name} is not in defined argument names {defined_argument_names}.",
                    MessageLevel.ERROR,
                    definition.source.uri,
                    None,
                )
                return ExecutionResult(
                    plugin_name,
                    "Check arguments against constraint definition",
                    ExecutionStatus.GENERAL_FAILURE,
                    [error_msg],
                )

    return ExecutionResult(
        plugin_name,
        "Check arguments against constraint definition",
        ExecutionStatus.SUCCESS,
        [],
    )
