"""The entry-point for the command line interface for the aac tool."""

import sys
from os import linesep
from click import (
    Argument,
    Command,
    Option,
    ParamType,
    Parameter,
    Path,
    UNPROCESSED,
    group,
    secho,
    types,
)

from aac.execute.plugin_runner import AacCommand, AacCommandArgument, PluginRunner
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    OperationCancelled,
    MessageLevel,
)
from aac.context.language_error import LanguageError
from aac.context.language_context import LanguageContext
from aac.in_out.parser._parser_error import ParserError

from typing import Callable


@group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """The Architecture-as-Code (AaC) command line tool."""
    pass


@cli.result_callback()
def output_result(result: ExecutionResult):
    """Output the result of the command."""
    error_occurred = not result.is_success()
    secho(result.get_messages_as_string(), err=error_occurred, color=True)

    if error_occurred:
        sys.exit(result.status_code.value)


def to_click_type(type_name: str) -> ParamType:
    """Convert the named type to a type recognized by Click."""
    if type_name == "file":
        return Path(file_okay=True)
    elif type_name == "directory":
        return Path(dir_okay=True)

    return types.__dict__.get(type_name.upper(), UNPROCESSED)


def to_click_parameter(argument: AacCommandArgument) -> Parameter:
    """Convert an AacCommandArgument to a Click Parameter."""
    names = [argument.name] if isinstance(argument.name, str) else argument.name
    args = dict(
        type=to_click_type(argument.data_type), nargs=1, default=argument.default
    )
    return (
        Option(
            names,
            help=argument.description,
            show_default=True,
            is_flag=argument.data_type == "bool",
            **args,
        )
        if argument.name[0].startswith("-")
        else Argument(names, **args)
    )


def handle_exceptions(plugin_name: str, func: Callable) -> Callable:  # noqa: C901
    """Decorator to catch and handle exceptions in a function."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LanguageError as e:
            return ExecutionResult(
                plugin_name,
                "exception",
                ExecutionStatus.GENERAL_FAILURE,
                [ExecutionMessage(e.message, MessageLevel.ERROR, None, e.location)],
            )
        except OperationCancelled as e:
            return ExecutionResult(
                plugin_name,
                "exception",
                ExecutionStatus.OPERATION_CANCELLED,
                [ExecutionMessage(str(e), MessageLevel.ERROR, None, None)],
            )
        except ParserError as e:
            usr_msg = f"The AaC file '{e.source}' could not be parsed.{linesep}"
            if e.errors:
                usr_msg = f"{usr_msg}The following errors were encountered:{linesep}"
                for err in e.errors:
                    usr_msg += f"  - {err}{linesep}"
            if e.yaml_error:
                usr_msg += f"The following YAML errors were encountered:{linesep}"
                exc = e.yaml_error
                if hasattr(exc, "problem_mark"):
                    if exc.context is not None:
                        usr_msg += f"  Parser Location: {str(exc.problem_mark)} - Problem: {str(exc.problem)} - Context: {str(exc.context)}{linesep}Please correct data and retry."
                    else:
                        usr_msg += f"  Parser Location: {str(exc.problem_mark)} - Problem: {str(exc.problem)}{linesep}Please correct data and retry."
            return ExecutionResult(
                plugin_name,
                "exception",
                ExecutionStatus.PARSER_FAILURE,
                [ExecutionMessage(usr_msg, MessageLevel.ERROR, None, None)],
            )

    return wrapper


def to_click_command(plugin_name: str, command: AacCommand) -> Command:
    """Convert an AacCommand to a Click Command."""

    def is_required_arg(arg):
        if isinstance(arg, list):
            return is_required_arg(arg[0])

        return not arg.name.startswith("-")

    return Command(
        name=command.name,
        callback=handle_exceptions(plugin_name, command.callback),
        params=[to_click_parameter(arg) for arg in command.arguments],
        short_help=command.description,
        no_args_is_help=len([arg for arg in command.arguments if is_required_arg(arg)])
        > 0,
    )


def initialize_cli():
    """Initialize the CLI."""
    try:
        active_context = LanguageContext()
    except LanguageError as e:
        if e.location:
            secho(f"{e.message}{linesep}{e.location}", err=True, color=True)
        else:
            secho(f"{e.message}", err=True, color=True)
        sys.exit(1)

    def get_commands() -> list[AacCommand]:
        result: list[AacCommand] = []

        context = LanguageContext()
        for runner in context.get_plugin_runners():
            definition = runner.plugin_definition
            for plugin_command in definition.instance.commands:
                arguments: list[AacCommandArgument] = []
                for input in plugin_command.input:
                    arguments.append(
                        AacCommandArgument(
                            input.name,
                            input.description,
                            context.get_python_type_from_primitive(input.type),
                            input.default,
                        )
                    )
                result.append(
                    AacCommand(
                        plugin_command.name,
                        plugin_command.help_text,
                        runner.command_to_callback[plugin_command.name],
                        arguments,
                    )
                )
        return result

    runners: list[PluginRunner] = active_context.get_plugin_runners()
    for runner in runners:
        commands = [
            to_click_command(runner.get_plugin_name(), cmd) for cmd in get_commands()
        ]
        for command in commands:
            cli.add_command(command)


# This is the entry point for the CLI
initialize_cli()
