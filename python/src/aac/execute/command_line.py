"""The entry-point for the command line interface for the aac tool."""

import sys, yaml
from click import Argument, Command, Option, ParamType, Parameter, Path, UNPROCESSED, group, secho, types

from aac.execute.plugin_runner import AacCommand, AacCommandArgument, PluginRunner
from aac.execute.aac_execution_result import ExecutionResult
from aac.context.language_context import LanguageContext
from aac.io.parser._parser_error import ParserError


@group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """The Architecture-as-Code (AaC) command line tool."""
    pass


@cli.result_callback()
def output_result(result: ExecutionResult):
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
    args = dict(type=to_click_type(argument.data_type), nargs=1, default=argument.default)
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
        short_help=command.description,
        no_args_is_help=len([arg for arg in command.arguments if is_required_arg(arg)]) > 0,
    )

def initialize_cli():
    active_context = LanguageContext()

    def get_commands() -> list[AacCommand]:
        result: list[AacCommand] = []

        context = LanguageContext()
        for runner in context.get_plugin_runners():
            definition = runner.plugin_definition
            for plugin_command in definition.instance.commands:
                arguments: list[AacCommandArgument] = []
                for input in plugin_command.input:
                    arguments.append(AacCommandArgument(
                        input.name, 
                        input.description, 
                        context.get_python_type_from_primitive(input.type), 
                        input.default))
                result.append(AacCommand(
                    plugin_command.name,
                    plugin_command.help_text,
                    runner.command_to_callback[plugin_command.name],
                    arguments,
                ))
        return result

    try:
        runners: list[PluginRunner] = active_context.get_plugin_runners()
        for runner in runners:
            commands = [to_click_command(cmd) for cmd in get_commands()]
            for command in commands:
                cli.add_command(command)
    except ParserError as error:
        exc = error.yaml_error
        print (f"Error while parsing YAML file: {error.source}")
        if hasattr(exc, 'problem_mark'):
            if exc.context != None:
                print ('  parser says\n' + str(exc.problem_mark) + '\n  ' +
                    str(exc.problem) + ' ' + str(exc.context) +
                    '\nPlease correct data and retry.')
            else:
                print ('  parser says\n' + str(exc.problem_mark) + '\n  ' +
                    str(exc.problem) + '\nPlease correct data and retry.')
        else:
            print (f"Something went wrong while parsing yaml file: {error.source}")

# This is the entry point for the CLI
initialize_cli()