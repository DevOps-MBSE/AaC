"""The entry-point for the command line interface for the aac tool."""

import sys
from click import Argument, Command, Option, ParamType, Parameter, Path, UNPROCESSED, echo, group, types

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins.plugin_execution import PluginExecutionResult
from aac.plugins.plugin_manager import get_plugin_commands


@group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """The Architecture-as-Code (AaC) command line tool."""
    pass


@cli.result_callback()
def output_result(result: PluginExecutionResult):
    error_occurred = not result.is_success
    echo(result.get_messages_as_string(), err=error_occurred, color=True)
    if error_occurred:
        sys.exit(result.status_code.value)


def to_click_type(type_name: str) -> ParamType:
    if type_name == "file":
        return Path(file_okay=True)
    elif type_name == "directory":
        return Path(dir_okay=True)

    return types.__dict__.get(type_name.upper(), UNPROCESSED)


def to_click_parameter(argument: AacCommandArgument) -> Parameter:
    names = [argument.name] if isinstance(argument.name, str) else argument.name
    args = dict(type=to_click_type(argument.data_type), nargs=argument.number_of_arguments, default=argument.default)
    return (
        Option(names, help=argument.description, show_default=True, **args)
        if argument.name[0].startswith("-")
        else Argument(names, **args)
    )


def to_click_command(command: AacCommand) -> Command:
    return Command(
        name=command.name,
        callback=command.callback,
        params=[to_click_parameter(arg) for arg in command.arguments],
        help=command.description,
        no_args_is_help=len(command.arguments) > 0,
    )


commands = [to_click_command(cmd) for cmd in get_plugin_commands()]
for command in commands:
    cli.add_command(command)
