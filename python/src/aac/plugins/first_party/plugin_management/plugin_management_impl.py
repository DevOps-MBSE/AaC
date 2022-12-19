"""AaC Plugin implementation module for the plugin-management plugin."""

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

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
        plugins = []
        active_context = get_active_context()
        if active:
            plugins = active_context.get_active_plugins()
        elif inactive:
            plugins = active_context.get_inactive_plugins()
        elif all:
            plugins = active_context.plugins

        return "\n".join([plugin.name for plugin in plugins])

    if len([arg for arg in [all, active, inactive] if arg]) > 1:
        raise PluginError(f"Flags are mutually-exclusive - got all: {all}; actived: {active}; inactive: {inactive}")

    with plugin_result(plugin_name, collect_plugins) as result:
        return result


def activate_plugin(plugin_name: str) -> PluginExecutionResult:
    """
    Activate a plugin that's available and inactive on the system.

    Args:
        plugin_name (str): The name of the plugin to be activated.
    """

    def _implement_and_rename_me():
        raise NotImplementedError("activate_plugin is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def deactivate_plugin(plugin_name: str) -> PluginExecutionResult:
    """
    Deactivate a plugin that's available and active on the system.

    Args:
        plugin_name (str): The name of the plugin to be deactivated.
    """

    def _implement_and_rename_me():
        raise NotImplementedError("deactivate_plugin is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result
