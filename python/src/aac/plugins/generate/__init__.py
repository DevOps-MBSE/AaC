"""The version plugin module."""

from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand, AacCommandArgument
from aac.plugins.generate.generate_impl import plugin_name, generate
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
# from aac.lang.plugin import Plugin
from aac.execute.plugin_runner import PluginRunner
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

GEN_PLUGIN_AAC_FILE_NAME = "generate.aac"

def run_generate(aac_plugin_file: str, generator_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool, force_overwrite: bool) -> ExecutionResult:
    """Run the AaC Gen-Plugin command."""

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])
    generate_result = generate(aac_plugin_file, generator_file, code_output, test_output, doc_output, no_prompt, force_overwrite)
    if not generate_result.is_success():
        return generate_result
    else:
        result.add_messages(generate_result.messages)

    return result

@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    active_context = LanguageContext()
    generate_aac_file = join(dirname(__file__), GEN_PLUGIN_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(generate_aac_file)
    
    generate_definition = [definition for definition in definitions if definition.name == plugin_name][0]

    plugin_instance = generate_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)
    
    plugin_runner = PluginRunner(plugin_definition=generate_definition)
    plugin_runner.add_command_callback("generate", run_generate)
    
    active_context.register_plugin_runner(plugin_runner)
