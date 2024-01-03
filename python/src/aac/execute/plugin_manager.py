"""Provide access to plugins and plugin data."""

from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from pluggy import PluginManager
from typing import List

from aac.execute import PLUGIN_PROJECT_NAME, hookspecs


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager and automatically register core plugins.

    Returns:
        The plugin manager.
    """
    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    plugins = [
        *register_plugins_in_package("aac.plugins"),
    ]

    for plugin in plugins:
        plugin_manager.register(plugin)

    return plugin_manager


def register_plugins_in_package(package: str) -> List[ModuleType]:
    """
    Register all the plugins in the specified package.

    Note, this function depends on the ability to import package and its direct child packages.

    Args:
        package (str): The package in which to find plugins to be registered.

    Returns:
        A list of top-level plugin modules that define implemented plugins.
    """
    plugins_package = import_module(package)
    return [import_module(f"{package}.{module_name}") for _, module_name, _ in iter_modules(plugins_package.__path__)]
