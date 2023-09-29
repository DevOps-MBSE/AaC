"""__init__.py module for the Version2 plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand


from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus
from aac.plugins.version2.version2_impl import plugin_name, version2

from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import PluginRunner

version2_aac_file_name = "version2.aac"


def run_version2() -> ExecutionResult:
    """Just a dupe of version for testing purposes"""

    result = ExecutionResult(plugin_name, "version2", ExecutionStatus.SUCCESS, [])

    version2_result = version2()
    if not version2_result.is_success():
        return version2_result
    else:
        result.add_messages(version2_result.messages)

    return result


@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    active_context = LanguageContext()
    version2_aac_file = join(dirname(__file__), version2_aac_file_name)
    definitions = active_context.parse_and_load(version2_aac_file)
    
    version2_plugin_definition = [definition for definition in definitions if definition.name == plugin_name][0]

    plugin_instance = version2_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)
    
    plugin_runner = PluginRunner(plugin_definition=version2_plugin_definition)
    
    plugin_runner.add_command_callback("version2", version2)
    
    
    active_context.register_plugin_runner(plugin_runner)