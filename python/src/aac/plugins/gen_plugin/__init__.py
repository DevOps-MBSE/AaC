"""The version plugin module."""

from os.path import join, dirname
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import PluginRunner
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

from aac.plugins.gen_plugin.gen_plugin_impl import plugin_name, gen_plugin, after_gen_plugin_generate
from aac.plugins.generate import run_generate

GEN_PLUGIN_AAC_FILE_NAME = "gen_plugin.aac"

def run_gen_plugin(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool) -> ExecutionResult:
    """Run the AaC Gen-Plugin command."""
    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])
    gen_plugin_result = gen_plugin(aac_plugin_file, code_output, test_output, doc_output, no_prompt)
    if not gen_plugin_result.is_success():
        return gen_plugin_result
    else:
        result.add_messages(gen_plugin_result.messages)

    generate_result = after_gen_plugin_generate(aac_plugin_file, code_output, test_output, doc_output, no_prompt, run_generate)
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
    gen_plugin_aac_file = join(dirname(__file__), GEN_PLUGIN_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(gen_plugin_aac_file)
    
    gen_plugin_plugin_definition = [definition for definition in definitions if definition.name == plugin_name][0]

    plugin_instance = gen_plugin_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)
    
    plugin_runner = PluginRunner(plugin_definition=gen_plugin_plugin_definition)
    plugin_runner.add_command_callback("gen-plugin", run_gen_plugin)
    
    active_context.register_plugin_runner(plugin_runner)
