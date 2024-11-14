"""General purpose steps for the behave BDD tests."""""
from behave import given, when, then, use_step_matcher
import os
from aac.context.language_context import LanguageContext
from aac.execute.command_line import cli, initialize_cli
from click.testing import CliRunner
from typing import Tuple

use_step_matcher("cfparse")


def run_cli_command_with_args(command_name: str, args: list[str]) -> Tuple[int, str]:
    """
    Utility function to invoke the CLI command with the given arguments.

    Args:
        command_name (str): CLI command to be executed.
        args (list[str]): List of arguments associated with the CLI command.

    Return:
        Exit code and output message resulting from the execution of the CLI command.
    """
    initialize_cli()
    runner = CliRunner()
    result = runner.invoke(cli, [command_name] + args)
    exit_code = result.exit_code
    std_out = str(result.stdout)
    output_message = std_out.strip().replace("\x1b[0m", "")
    return exit_code, output_message


@given('I have the "{file}" file')
def given_model(context, file: str):
    """
    Ensure the given model file exists.

    Args:
        context: Active context to check against.
        file (str): Path to the file being evaluated.
    """
    if not os.path.exists(file):
        raise AssertionError(f"File path {file} does not exist")


@when('I run the "{command}" command with no arguments and with no flags')
def command_no_args_no_flags(context, command):
    """
    Runs a command with specified flags and no arguments.

    Args:
        context: Active context to check against.
        command: Command being run.
    """
    exit_code, output_message = run_cli_command_with_args(command, [])
    context.exit_code = exit_code
    context.output_message = output_message


@when('I run the "{command}" command with arguments "{args}" and with no flags')
def command_args_no_flags(context, command, args):
    """
    Runs a command with specified flags and no arguments.

    Args:
        context: Active context to check against.
        command: Command being run.
        args: Specified Arguments
    """
    args_list = args.split()
    exit_code, output_message = run_cli_command_with_args(command, args_list)
    context.exit_code = exit_code
    context.output_message = output_message


@when('I run the "{command}" command with no arguments and with flags "{flags}"')
def command_flags_no_args(context, command, flags):
    """
    Runs a command with specified flags and no arguments.

    Args:
        context: Active context to check against.
        command: Command being run.
        flags: Specified Flags.
    """
    flags_list = flags.split()

    exit_code, output_message = run_cli_command_with_args(command, flags_list)
    context.exit_code = exit_code
    context.output_message = output_message


@when('I run the "{command}" command with arguments "{args}" and with flags "{flags}"')
def command_args_flags(context, command, args, flags):
    """
    Runs a command with specified flags and no arguments.

    Args:
        context: Active context to check against.
        command: Command being run.
        args: Specified Arguments
        flags: Specified Flags.
    """
    args_list = args.split()
    flags_list = flags.split()

    exit_code, output_message = run_cli_command_with_args(command, args_list + flags_list)
    context.exit_code = exit_code
    context.output_message = output_message


@when(u'I load the "{file_path}" file')
def load_model(context, file_path):
    """
    Load a model file and put it into the context.

    Args:
        context: Active context to check against.
        model_file: Path of model file to load.
    """
    try:
        aac_context = LanguageContext()
        definitions = aac_context.parse_and_load(file_path)
        context.aac_loaded_definitions = definitions
    except Exception as e:
        raise AssertionError(f"Failed to load model file {model_file} with exception {e}")


@then("I should receive a message that the command was successful")
def command_success(context):
    """
    Ensure the command was successful.

    Args:
        context: Active context to check against.
    """
    assert context.exit_code == 0
    assert "success" or "Success" or "successfully" in context.output_message


@then("I should receive a message that the command was not successful")
def command_failure(context):
    """
    Ensure the command was not successful.

    Args:
        context: Active context to check against.
    """
    assert context.exit_code != 0
    assert "All AaC constraint checks were successful" not in context.output_message


@then("I should receive a list of successfully evaluated models")
def verbose_check(context):
    """
    Ensure the check command with verbose ran returned the list of models.

    Args:
        context: Active context to check against.
    """
    assert ("was successful." in context.output_message)  # only appears when using verbose


@then(u'I should have {count} total {root_key} definitions')
def check_count_by_root_key(context, count, root_key):
    """
    Evaluate the number of root_key items parsed from a model.

    Args:
        context: Active context to check against.
        count: The number of definitions loaded from the model.
        root_key:  The root_key for the definitions of interest.
    """
    items = []
    for definition in context.aac_loaded_definitions:
        if definition.get_root_key() == root_key:
            items.append(definition)

    if len(items) != int(count):
        raise AssertionError(
            f"Found {len(items)} with root_key {root_key}, but expected {count}."
        )

@then(u'I should have requirement id {req_id}')
def check_req_id(context, req_id):
    """
    Evaluate the expected req ids are present in the parsed items.

    Args:
        context: Active context to check against.
        req_id_list: A list of req id values.
    """
    print("DEBUG: running 'I should have requirement ids' step_impl for {req_id}")
    parsed_ids = []
    for definition in context.aac_loaded_definitions:
        if definition.get_root_key() == "req":
            parsed_ids.append(definition.instance.id)
    if req_id not in parsed_ids:
        raise AssertionError(f"Expected id {req_id} not found in parsed req ids.")
