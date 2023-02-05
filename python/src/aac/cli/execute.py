"""The entry-point for the command line interface for the aac tool."""

import sys
from click import Argument, Command, Option, ParamType, Parameter, Path, UNPROCESSED, echo, group, types

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.persistence import ACTIVE_CONTEXT_STATE_FILE_NAME
from aac.plugins.plugin_execution import PluginExecutionResult


@group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """The Architecture-as-Code (AaC) command line tool."""
    pass


@cli.result_callback()
def output_result(result: PluginExecutionResult):
    """Output the message from the result of executing the CLI command."""
    error_occurred = not result.is_success()
    echo(result.get_messages_as_string(), err=error_occurred, color=True)

    get_active_context().export_to_file(ACTIVE_CONTEXT_STATE_FILE_NAME)

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
    args = dict(type=to_click_type(argument.data_type), nargs=argument.number_of_arguments, default=argument.default)
    return (
        Option(names, help=argument.description, show_default=True, is_flag=argument.data_type == "bool", **args)
        if argument.name[0].startswith("-")
        else Argument(names, **args)
    )


def to_click_command(command: AacCommand) -> Command:
    """Convert an AacCommand to a Click Command."""

    def is_required_arg(arg):
        if isinstance(arg, list):
            return is_required_arg(arg[0])

        return not arg.name.startswith("-")

    return Command(
        name=command.name,
        callback=command.callback,
        params=[to_click_parameter(arg) for arg in command.arguments],
        help=command.description,
        no_args_is_help=len([arg for arg in command.arguments if is_required_arg(arg)]) > 0,
    )


active_context = get_active_context()
commands = [to_click_command(cmd) for cmd in active_context.get_plugin_commands()]
for command in commands:
    cli.add_command(command)
