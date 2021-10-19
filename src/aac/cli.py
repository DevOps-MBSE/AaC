"""
The command line processor for aac.
"""
import argparse
import itertools
import inspect

from typing import Callable
from pluggy import PluginManager

from aac import genjson, genplug, validator, parser, util, hookspecs, PLUGIN_PROJECT_NAME
from aac.AacCommand import AacCommand, AacCommandArgument


def run_cli():
    """
    The main entry point for aac.

    This method parses the command line and performs the
    requested user command...or outputs usage.
    """

    plugin_manager = _get_plugin_manager()

    arg_parser, aac_plugin_commands = _setup_arg_parser(plugin_manager)

    # apply plugin extensions
    results = plugin_manager.hook.get_base_model_extensions()
    for plugin_ext in results:
        if len(plugin_ext) > 0:
            parsed = parser.parse_str(plugin_ext, "Plugin Manager Addition", True)
            util.extend_aac_spec(parsed)

    args = arg_parser.parse_args()

    for command in aac_plugin_commands:
        if args.command == command.name:

            keyword_args = {}
            args_dict = vars(args)

            # Leverage inspect here to make sure that the arg names we're trying to access are sourced from the target function itself
            parameters = inspect.signature(command.callback).parameters.keys()
            for argument in parameters:
                keyword_args[argument] = args_dict[argument]

            command.callback(**keyword_args)


def _validate_cmd(yaml: str):
    """The built-in validate command."""
    parsed_model = parser.parse_file(yaml, False)
    valid, error_list = validator.validate(parsed_model)

    if valid:
        print(f"Model [{yaml}] is valid")
    else:
        print(f"Model [{yaml}] is invalid. \n{error_list}")


def _core_spec_cmd():
    """The built-in aac-core-spec command."""
    print(util.get_aac_spec_as_yaml())


def _setup_arg_parser(
    plugin_manager: PluginManager,
) -> tuple[argparse.ArgumentParser, list[Callable]]:
    arg_parser = argparse.ArgumentParser()
    command_parser = arg_parser.add_subparsers(dest="command")

    # Built-in commands
    aac_commands = [
        AacCommand(
            "validate",
            "Ensures the AaC yaml is valid per the AaC core spec",
            _validate_cmd,
            [AacCommandArgument("yaml", "The path to your AaC yaml")],
        ),
        AacCommand(
            "aac-core-spec",
            "Prints the AaC model describing core AaC data types and enumerations",
            _core_spec_cmd,
        ),
    ]

    results = plugin_manager.hook.get_commands()
    aac_and_plugin_commands = aac_commands + list(itertools.chain(*results))

    for command in aac_and_plugin_commands:
        command_subparser = command_parser.add_parser(command.name, help=command.description)

        for argument in command.arguments:
            command_subparser.add_argument(
                argument.name, help=argument.description, nargs=argument.number_of_arguments
            )

    return arg_parser, aac_and_plugin_commands


def _get_plugin_manager():
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" plugins
    plugin_manager.register(genjson)
    plugin_manager.register(genplug)

    return plugin_manager
