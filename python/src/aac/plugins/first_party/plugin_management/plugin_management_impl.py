"""AaC Plugin implementation module for the plugin-management plugin."""

import logging

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.plugins.plugin_manager import get_plugins

plugin_name = "plugin-management"


def list_plugins(all: bool, active: bool, inactive: bool) -> PluginExecutionResult:
    """
    Display a list of available plugins.

    Args:
        all (bool): Display a list of all the installed AaC plugins.
        active (bool): Display a list of all the active AaC plugins.
        inactive (bool): Display a list of all the inactive AaC plugins.

    Returns:
        plugins The list of plugin names.
    """

    def collect_plugins():
        return "\n".join(_get_plugin_names(all=all, active=active, inactive=inactive))

    with plugin_result(plugin_name, collect_plugins) as result:
        return result


def activate_plugin(name: str) -> PluginExecutionResult:
    """
    Activate a plugin that's available and inactive on the system.

    Args:
        name (str): The name of the plugin to be activated.
    """

    def activate_named_plugin() -> str:
        if name not in _get_plugin_names(all=True):
            raise PluginError(f"Plugin {name} cannot be activated because it is not installed")
        elif name in _get_plugin_names(active=True):
            raise PluginError(f"Plugin {name} is already active")

        get_active_context().activate_plugin_by_name(name)

        activation_message = f"Successfully activated plugin: {name}"
        logging.info(activation_message)
        return activation_message

    with plugin_result(plugin_name, activate_named_plugin) as result:
        return result


def deactivate_plugin(name: str) -> PluginExecutionResult:
    """
    Deactivate a plugin that's available and active on the system.

    Args:
        name (str): The name of the plugin to be deactivated.
    """

    def deactivate_named_plugin() -> str:
        if name not in _get_plugin_names(all=True):
            raise PluginError(f"Plugin {name} cannot be deactivated because it is not installed")
        elif name in _get_plugin_names(inactive=True):
            raise PluginError(f"Plugin {name} is already inactive")

        get_active_context().deactivate_plugin_by_name(name)

        deactivation_message = f"Successfully deactivated plugin: {name}"
        logging.info(deactivation_message)
        return deactivation_message

    with plugin_result(plugin_name, deactivate_named_plugin) as result:
        return result


def _get_plugin_names(*, all: bool = False, active: bool = False, inactive: bool = False) -> list[str]:
    """
    Return the names of the specified plugins.

    All arguments are mutually exclusive.

    Args:
        all (bool): Whether to get all the plugin names, or not.
        active (bool): Whether to get active the plugin names, or not.
        inactive (bool): Whether to get inactive the plugin names, or not.

    Returns:
        A list of the requested plugin names.
    """
    plugins = []
    active_context = get_active_context()
    option_name, _ = _get_selected_option(all=all, active=active, inactive=inactive)

    if option_name == "all":
        plugins = get_plugins()
    elif option_name == "active":
        plugins = active_context.get_active_plugins()
    elif option_name == "inactive":
        plugins = active_context.get_inactive_plugins()

    return [plugin.name for plugin in plugins]


def _get_selected_option(**kwargs) -> tuple[str, bool]:
    """
    Return the option if only one option was provided; otherwise, raise an error.

    Returns:
        Return the option whose value is True.

    Raises:
        A PluginError is raised if more than one option is provided or no options are provided.
    """
    options = _provided_options(**kwargs)
    if len(options) > 1:
        formatted_options = "; ".join([f"{name}={val}" for name, val in options])
        raise PluginError(f"Multiple mutually-exclusive options provided: {formatted_options}")
    elif len(options) < 1:
        raise PluginError("No option provided")

    return options[0]


def _provided_options(**kwargs) -> list[tuple[str, bool]]:
    """Return the provided option(s)."""
    return [(key, val) for key, val in kwargs.items() if val]
