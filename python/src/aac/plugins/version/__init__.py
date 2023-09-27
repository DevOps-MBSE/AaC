"""The version plugin module."""

from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand
from aac.plugins.version.version_impl import plugin_name, version
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import PluginRunner
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

VERSION_AAC_FILE_NAME = "version.aac"

def run_version() -> ExecutionResult:
    """Print the AaC package version."""

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])

    version_result = version()
    if not version_result.is_success():
        return version_result
    else:
        result.add_messages(version_result.messages)

    return result

@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    active_context = LanguageContext()
    version_aac_file = join(dirname(__file__), VERSION_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(version_aac_file)
    
    version_plugin_definition = [definition for definition in definitions if definition.name == plugin_name][0]
    
    plugin_runner = PluginRunner(plugin_definition=version_plugin_definition)
    plugin_runner.add_command_callback("version", run_version)
    
    active_context.register_plugin_runner(plugin_runner)
