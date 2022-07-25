"""Provide access to plugins and plugin data."""
from importlib import import_module
from iteration_utilities import flatten
from pluggy import PluginManager
import itertools

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.io.parser import parse
from aac.plugins import hookspecs, PLUGIN_PROJECT_NAME
from aac.plugins.plugin import Plugin
from aac.plugins.validators import ValidatorPlugin


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager and automatically registers internal plugins.

    Returns:
        The plugin manager.
    """
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" plugins
    first_party_plugins_package = "aac.plugins"
    first_party_plugins = [
        "gen_json",
        "gen_plugin",
        "gen_protobuf",
        "gen_design_doc",
        "gen_gherkin_behaviors",
        "gen_plant_uml",
        "specifications",
        "print_spec",
        "start_lsp",
        "material_model",
        "help_dump",
        "rest_api",
    ]

    # register "built-in" commands
    builtin_command_plugins_package = "aac.cli.builtin_commands"
    builtin_command_plugins = [
        "validate",
        "version",
    ]

    # register "built-in" validation plugins
    validator_plugins_package = "aac.plugins.validators"
    validator_plugins = [
        "defined_references",
        "required_fields",
        "validator_implementation",
        "exclusive_fields",
        "subcomponent_type",
        "root_keys",
        "reference_fields",
        "reference_targets",
    ]

    def register_plugin(plugin, package):
        plugin_module = import_module(f"{package}.{plugin}")
        plugin_manager.register(plugin_module)

    [register_plugin(name, first_party_plugins_package) for name in first_party_plugins]
    [register_plugin(name, builtin_command_plugins_package) for name in builtin_command_plugins]
    [register_plugin(name, validator_plugins_package) for name in validator_plugins]

    return plugin_manager


def get_plugin_definitions() -> list[Definition]:
    """
    Get a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of parsed definitions from all active plugins.
    """

    def set_files_to_not_user_editable(definition):
        definition.source.is_user_editable = False
        return definition

    plugins = get_plugin_manager().hook.get_plugin()
    flattened_definition_list = list(flatten(filter(lambda x: x, [plugin.get_definitions() for plugin in plugins])))
    return list(map(set_files_to_not_user_editable, flattened_definition_list))


def get_validator_plugins() -> list[ValidatorPlugin]:
    """
    Get a list of registered validator plugins and metadata.

    Returns:
        A list of validator plugins that are currently registered.
    """
    return get_plugin_manager().hook.register_validators()


def get_plugins() -> list[Plugin]:
    """
    Get a list of all the plugins available in the AaC package.

    Returns:
        A list of plugins that are currently registered.
    """
    plugin_manager = get_plugin_manager()
    plugin_models_yaml = plugin_manager.hook.get_plugin_aac_definitions()
    plugin_extensions = {}
    for plugin_ext in plugin_models_yaml:
        if len(plugin_ext) > 0:
            parsed_definitions = parse(plugin_ext)
            definitions_dict = dict(map(lambda definition: (definition.name, definition.structure), parsed_definitions))
            plugin_extensions = definitions_dict | plugin_extensions

    return plugin_extensions


def get_plugin_commands() -> list[AacCommand]:
    """Return all of the AaC Commands provided by plugins."""
    plugin_manager = get_plugin_manager()
    plugin_commands = plugin_manager.hook.get_commands()
    return list(itertools.chain(*plugin_commands))
    return get_plugin_manager().hook.get_plugin()
