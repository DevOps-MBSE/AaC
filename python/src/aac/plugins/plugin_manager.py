"""Provide access to plugins and plugin data."""

from importlib import import_module
from typing import List

from pluggy import PluginManager

from aac.plugins import PLUGIN_PROJECT_NAME, Plugin, hookspecs

# Using an installed plugin cache for performance. This will causes issues if
# users try to install new plugins without restarting AaC.

INSTALLED_PLUGINS: List[Plugin] = []


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager and automatically registers first-party internal plugins.

    Returns:
        The plugin manager.
    """
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # Register 1st Party Plugins because pluggy doesn't provide an alternative
    # solution to automatically register plugins that are packaged in the AaC
    # package.

    # register "built-in" plugins
    first_party_plugins_package = "aac.plugins.first_party"
    first_party_plugins = [
        "gen_json",
        "gen_plugin",
        "gen_protobuf",
        "gen_design_doc",
        "gen_gherkin_behaviors",
        "gen_plant_uml",
        "print_spec",
        "lsp_server",
        "help_dump",
        "rest_api",
        "primitive_type_check",
        "plugin_management",
        "active_context",
    ]

    # register "built-in" commands
    builtin_command_plugins_package = "aac.cli.builtin_commands"
    builtin_command_plugins = [
        "specifications",
        "validate",
        "version",
    ]

    # register "built-in" validation plugins
    validator_plugins_package = "aac.plugins.validators"
    validator_plugins = [
        "defined_references",
        "exclusive_fields",
        "reference_fields",
        "reference_targets",
        "required_fields",
        "requirement_references",
        "root_keys",
        "subcomponent_type",
        "unique_names",
        "unique_requirement_ids",
        "unused_definitions",
        "validator_implementation",
    ]

    plugins = [
        *zip([first_party_plugins_package] * len(first_party_plugins), first_party_plugins),
        *zip([builtin_command_plugins_package] * len(builtin_command_plugins), builtin_command_plugins),
        *zip([validator_plugins_package] * len(validator_plugins), validator_plugins),
    ]

    for package, plugin in plugins:
        plugin_module = import_module(f"{package}.{plugin}")
        plugin_manager.register(plugin_module)

    return plugin_manager


def get_plugins() -> list[Plugin]:
    """
    Get a list of all the system-wide plugins available to activate in the AaC package.

    Returns:
        A list of plugins that are currently installed on the system.
    """
    global INSTALLED_PLUGINS
    if not INSTALLED_PLUGINS:
        INSTALLED_PLUGINS = get_plugin_manager().hook.get_plugin()

    return [plugin.copy() for plugin in INSTALLED_PLUGINS]
