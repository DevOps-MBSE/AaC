"""AaC Plugin implementation module for the plugin-management plugin."""

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

    def _implement_and_rename_me():
        raise NotImplementedError("list_plugins is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
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
