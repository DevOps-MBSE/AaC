"""AaC Plugin implementation module for the version plugin."""

from aac import __version__
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "version"


def version() -> PluginExecutionResult:
    """Print the AaC package version."""

    def get_current_version():
        return __version__

    with plugin_result(plugin_name, get_current_version) as result:
        return result
