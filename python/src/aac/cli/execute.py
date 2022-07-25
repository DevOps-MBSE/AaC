"""The entry-point for the command line interface for the aac tool."""
import argparse
import inspect
import sys
from typing import Callable

from aac.plugins.plugin_manager import get_plugin_commands


def run_cli():
    """
    Run the specified AaC command.

    This method parses the command line and performs the requested user command or outputs usage.
    """
    arg_parser, aac_plugin_commands = _setup_arg_parser()

    args = arg_parser.parse_args()

    for command in aac_plugin_commands:
        if args.command == command.name:

            keyword_args = {}
            args_dict = vars(args)

            # Leverage inspect here to make sure that the arg names we're trying to access are
            # sourced from the target function itself
            parameters = inspect.signature(command.callback).parameters.keys()
            for argument in parameters:
                if args_dict[argument] is not None:
                    keyword_args[argument] = args_dict[argument]

            result = command.callback(**keyword_args)
            print(f"{result.name}: {result.status_code.name.lower()}\n\n{result.get_messages_as_string()}")

            if not result.is_success():
                sys.exit(result.status_code.value)


def _setup_arg_parser() -> tuple[argparse.ArgumentParser, list[Callable]]:
    def help_formatter(prog):
        return argparse.HelpFormatter(prog, max_help_position=30)

    arg_parser = argparse.ArgumentParser(formatter_class=help_formatter)
    command_parser = arg_parser.add_subparsers(dest="command")

    aac_and_plugin_commands = get_plugin_commands()

    for command in aac_and_plugin_commands:
        command_subparser = command_parser.add_parser(command.name, help=command.description)

        for argument in command.arguments:
            command_subparser.add_argument(argument.name, help=argument.description, **_get_arguments(argument))

    return arg_parser, aac_and_plugin_commands


def _get_arguments(argument):
    arguments = {}
    if argument.action:
        arguments = arguments | {"action": argument.action}
    else:
        arguments = arguments | {"nargs": argument.number_of_arguments, "choices": argument.choices}

    return arguments
