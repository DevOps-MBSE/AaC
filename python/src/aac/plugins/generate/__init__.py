"""The version plugin module."""

from os.path import join, dirname
from aac.plugins.generate.generate_impl import plugin_name, generate, clean
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import PluginRunner
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus

GEN_PLUGIN_AAC_FILE_NAME = "generate.aac"


def run_generate(
    aac_plugin_file: str,
    generator_file: str,
    code_output: str,
    test_output: str,
    doc_output: str,
    no_prompt: bool,
    force_overwrite: bool,
    evaluate: bool,
) -> ExecutionResult:
    """Run the AaC generate command."""

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])
    generate_result = generate(
        aac_plugin_file,
        generator_file,
        code_output,
        test_output,
        doc_output,
        no_prompt,
        force_overwrite,
        evaluate,
    )
    if not generate_result.is_success():
        return generate_result
    else:
        result.add_messages(generate_result.messages)

    return result


def run_clean(
    aac_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool
) -> ExecutionResult:
    """Run the AaC clean command."""

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])
    generate_result = clean(aac_file, code_output, test_output, doc_output, no_prompt)
    if not generate_result.is_success():
        return generate_result
    else:
        result.add_messages(generate_result.messages)

    return result


@hookimpl
def register_plugin() -> None:
    """Registers the plugin with the AaC CLI."""

    active_context = LanguageContext()
    generate_aac_file = join(dirname(__file__), GEN_PLUGIN_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(generate_aac_file)

    generate_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = generate_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(plugin_definition=generate_definition)
    plugin_runner.add_command_callback("generate", run_generate)
    plugin_runner.add_command_callback("clean", run_clean)

    active_context.register_plugin_runner(plugin_runner)
