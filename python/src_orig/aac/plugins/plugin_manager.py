"""Provide access to plugins and plugin data."""

from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from pluggy import PluginManager
from typing import List

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

    plugins = [
        *register_plugins_in_package("aac.cli.builtin_commands"),
        *register_plugins_in_package("aac.plugins.first_party"),
        *register_plugins_in_package("aac.plugins.validators"),
    ]

    for plugin in plugins:
        plugin_manager.register(plugin)

    return plugin_manager


def register_plugins_in_package(package: str) -> List[ModuleType]:
    """
    Register all the plugins in the specified package.

    Note, this function depends on the ability to import package and it's direct child packages.

    Args:
        package (str): The package in which to find plugins to be registered.

    Returns:
        A list of top-level plugin modules that define implemented plugins.
    """
    plugins_package = import_module(package)
    return [import_module(f"{package}.{module_name}") for _, module_name, _ in iter_modules(plugins_package.__path__)]


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


def register_plugin(plugin: Plugin) -> None:
    """
    Manually register an AaC plugin object without leveraging Pluggy hooks.

    This function is intended to be used to manually register plugins after the plugin manager
        has been initialized. This function should be used for testing where plugins are manually registered.
        If you're using this function outside of a test then you should re-evaluate why your approach includes
        manual registration as opposed to using the documented plugin interface and registration methods that can
        be found in the official AaC documentation.
    """
    global INSTALLED_PLUGINS

    if isinstance(plugin, Plugin):
        INSTALLED_PLUGINS.append(plugin)


def clear_plugins() -> None:
    """
    Manually clear the installed AaC plugins.

    This function is intended to be used to manually clear registered plugins after the plugin manager
        has been initialized. This function should be used for testing where plugins are manually registered.
        If you're using this function outside of a test then you should re-evaluate why your approach includes
        manual clearing of registered plugins as opposed to using the documented plugin interface and registration
        methods that can be found in the official AaC documentation.
    """
    global INSTALLED_PLUGINS
    INSTALLED_PLUGINS = []
