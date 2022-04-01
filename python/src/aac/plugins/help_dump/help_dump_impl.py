"""AaC Plugin implementation module for the help-dump plugin."""

from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "help-dump"


def help_dump() -> PluginExecutionResult:
    """
    Produce a formatted string containing all commands, their arguments, and each of their descriptions.
.
    Returns:
        help_output (str): The formatted string with all commands, etc.
    """
    def _implement_and_rename_me():
        raise NotImplementedError("help_dump is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result
