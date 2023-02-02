"""Provide access to plugins and plugin data."""
from importlib import import_module
from pluggy import PluginManager

from aac.plugins import hookspecs, PLUGIN_PROJECT_NAME
from aac.plugins.plugin import Plugin


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager and automatically registers first-party internal plugins.

    Returns:
        The plugin manager.
    """
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # Register 1st Party Plugins because pluggy doesn't provide an alternative solution to automatically register plugins that are packaged in the AaC package.

    # register "built-in" plugins
    first_party_plugins_package = "aac.plugins.first_party"
    first_party_plugins = [
        "gen_json",
        "gen_plugin",
        "gen_protobuf",
        "gen_design_doc",
        "gen_gherkin_behaviors",
        "gen_plant_uml",
        "specifications",
        "print_spec",
        "lsp_server",
        "material_model",
        "help_dump",
        "rest_api",
        "primitive_type_check",
        "plugin_management",
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
        "unique_names",
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
