"""
The command line processor for aac.
"""
import argparse
import sys
import os
import itertools
from pluggy import PluginManager
from aac import genjson, genplug, parser, util, hookspecs, PLUGIN_PROJECT_NAME

list_suffix = "[]"
enum_types = {}
data_types = {}
model_types = {}


def run_CLI():
    """
    The main entry point for aac.  This method parses the command line and
    performs the requested user command...or outputs usage.
    """

    pm = _get_plugin_manager()

    # register "built-in" plugins
    pm.register(genjson)
    pm.register(genplug)

    arg_parser = argparse.ArgumentParser()
    command_parser = arg_parser.add_subparsers(dest="command")
    # the validate command is built-in
    command_parser.add_parser(
        "validate", help="Ensures the AaC yaml is valid per the AaC core spec"
    )
    # the print-spec command is built-in
    command_parser.add_parser(
        "aac-core-spec", help="Prints the AaC model describing core AaC data types and enumerations"
    )
    results = pm.hook.get_commands()
    aac_plugin_commands = list(itertools.chain(*results))
    for cmd in aac_plugin_commands:
        command_parser.add_parser(
            cmd.command_name, help=cmd.command_description
        )

    # apply plugin extensions
    results = pm.hook.get_base_model_extensions()
    for plugin_ext in results:
        if len(plugin_ext) > 0:
            parsed = parser.parseStr(plugin_ext, "Plugin Manager Addition", True)
            util.extend_aac_spec(parsed)

    arg_parser.add_argument("yaml", type=str, help="The path to your AaC yaml")

    args = arg_parser.parse_args()

    # this command is special, it shouldn't need any additional inputs
    if args.command == "aac-core-spec":
        print(util.get_aac_spec_as_yaml())
        return

    model_file = args.yaml
    if not os.path.isfile(model_file):
        print(f"{model_file} does not exist")
        arg_parser.print_usage()
        sys.exit()

    parsed_models = {}
    try:
        parsed_models = parser.parseFile(model_file)
    except RuntimeError:
        print(f"Model [{model_file}] is invalid")
        sys.exit("validation error")

    # validate is a built-in command - when called just print that the input model is valid
    if args.command == "validate":
        print(f"Model [{model_file}] is valid")

    for cmd in aac_plugin_commands:
        if args.command == cmd.command_name:
            cmd.callback(model_file, parsed_models)


def _get_plugin_manager():
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    return plugin_manager
