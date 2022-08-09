"""Provide access to plugins and plugin data."""
from importlib import import_module
from iteration_utilities import flatten
from pluggy import PluginManager

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
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


def get_plugins() -> list[Plugin]:
    """
    Get a list of all the plugins available in the AaC package.

    Returns:
        A list of plugins that are currently registered.
    """
    return get_plugin_manager().hook.get_plugin()


def get_plugin_commands() -> list[AacCommand]:
    """
    Get a list of all of the AaC commands contributed by plugins.

    Returns:
        A list of AaC Commands provided by plugins.
    """
    return list(flatten([plugin.get_commands() for plugin in get_plugins() if plugin.get_commands()]))


def get_plugin_definitions() -> list[Definition]:
    """
    Get a list of all the plugin-defined AaC definitions.

    Returns:
        A list of parsed definitions from all active plugins.
    """

    def set_files_to_not_user_editable(definition):
        definition.source.is_user_editable = False
        return definition

    definitions = [plugin.get_definitions() for plugin in get_plugins() if plugin.get_definitions()]
    return list(map(set_files_to_not_user_editable, flatten(definitions)))


def get_validator_plugins() -> list[ValidatorPlugin]:
    """
    Get a list of registered validator plugins and metadata.

    Returns:
        A list of validator plugins that are currently registered.
    """
    return list(flatten([plugin.get_validations() for plugin in get_plugins() if plugin.get_validations()]))
