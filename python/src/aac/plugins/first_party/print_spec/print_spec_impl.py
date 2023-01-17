"""AaC Plugin implementation module for the print-spec plugin."""

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.spec.core import get_aac_spec_as_yaml


plugin_name = "print-spec"


def print_spec() -> PluginExecutionResult:
    """Print the AaC model describing core AaC data types and enumerations."""
    with plugin_result(plugin_name, get_aac_spec_as_yaml) as result:
        return result


def print_active_context() -> PluginExecutionResult:
    """Print the AaC active language context including data types and enumerations added by plugins."""

    def print_active_context_as_yaml():
        active_context = get_active_context()
        return "---\n".join(map(lambda definition: definition.to_yaml(), active_context.definitions))

    with plugin_result(plugin_name, print_active_context_as_yaml) as result:
        return result
