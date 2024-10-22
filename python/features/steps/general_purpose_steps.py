"""General purpose steps for the behave BDD tests."""""
from behave import given, when, then, use_step_matcher
import os
from aac.execute.command_line import cli, initialize_cli
from click.testing import CliRunner
from shutil import rmtree
from typing import Tuple

use_step_matcher("cfparse")


def get_model_file(context, path: str) -> str:
    """
    Utility function to get the full path to the given model file.

    Args:
        context: Active context to check against.
        path (str): Path to the model file being evaluated.

    Return:
        Valid path for the requested model file as tracked within the context.
    """
    return os.path.sep.join([context.config.paths[0], path])


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


@given('I have the "{model_file}" model')
def given_model(context, model_file: str):
    """
    Ensure the given model file exists.

    Args:
        context: Active context to check against.
        model_file (str): Path to the model file being evaluated.
    """
    model_path = get_model_file(context, model_file)
    if not os.path.exists(model_path):
        raise AssertionError(f"Model file {model_path} does not exist")


@given('I have a valid "{plugin_file}"')
def gen_plugin_valid_check(context, plugin_file):
    """
    Run the check command on the given plugin file.

    Args:
        context: Active context to check against.
        plugin_file (str): Path to plugin file being used for generation.
    """
    plugin_file_path = get_model_file(context, plugin_file)
    exit_code, output_message = run_cli_command_with_args("check", [plugin_file_path])
    if exit_code != 0:
        raise AssertionError(f"Check cli command failed with message: {output_message}")
    context.plugin_file_path = plugin_file_path
    context.output_message = output_message


@when('I check the "{model_file}" model')
def check_model(context, model_file):
    """
    Run the check command on the given model.

    Args:
        context: Active context to check against.
        model_file (str): Path to the model file being evaluated.
    """
    exit_code, output_message = run_cli_command_with_args(
        "check", [get_model_file(context, model_file)]
    )
    if exit_code != 0:
        raise AssertionError(f"Check cli command failed with message: {output_message}")
    context.output_message = output_message


@when('I check the "{model_file}" model with verbose')
def check_model_verbose(context, model_file):
    """
    Run the check command on the given model with verbose.

    Args:
        context: Active context to check against.
        model_file (str): Path to the model file being evaluated.
    """
    exit_code, output_message = run_cli_command_with_args(
        "check", [get_model_file(context, model_file), "--verbose"]
    )
    if exit_code != 0:
        raise AssertionError(f"Check cli command failed with message: {output_message}")
    context.output_message = output_message


@when('I check the "{model_file}" bad model')
def check_model_fail(context, model_file):
    """
    Run the check command on the given model.

    Args:
        context: Active context to check against.
        model_file (str): Path to the model file being evaluated.
    """
    exit_code, output_message = run_cli_command_with_args(
        "check", [get_model_file(context, model_file)]
    )
    if exit_code == 0:
        raise AssertionError(f"Check cli command succeeded with message: {output_message}")
    context.output_message = output_message


@when("Gen-Plugin is ran with the valid plugin file")
def run_gen_plugin(context):
    """
    Run Gen-Plugin on a valid plugin file.

    Args:
        context: Active context to check against.
    """
    temp_dir = ("./temporary_directory")
    if os.path.exists(temp_dir):
        rmtree(temp_dir)
    os.makedirs(temp_dir)
    src_dir = os.path.join(temp_dir, "src")
    os.makedirs(src_dir)
    context.src_dir = src_dir
    test_dir = os.path.join(temp_dir, "tests")
    os.makedirs(test_dir)

    context.test_dir = test_dir
    context.temp_dir = temp_dir
    plugin_args = [context.plugin_file_path, "--code-output", src_dir, "--test-output", test_dir, "--no-prompt"]
    exit_code, output_message = run_cli_command_with_args(
        "gen-plugin", plugin_args)

    assert ("All AaC constraint checks were successful" in output_message)  # asserts the command ran check successfully
    context.output_message = output_message


@then("I should receive a message that the check was successful")
def check_success(context):
    """
    Ensure the check command was successful.

    Args:
        context: Active context to check against.
    """
    if "All AaC constraint checks were successful." not in context.output_message:
        raise AssertionError(
            f"Model check failed with message: {context.output_message}"
        )


@then("I should receive a message that the check was not successful")
def check_failure(context):
    """
    Ensure the check command was successful.

    Args:
        context: Active context to check against.
    """
    if "All AaC constraint checks were successful." in context.output_message:
        raise AssertionError(
            f"Model check succeeded with message: {context.output_message}"
        )


@then("I should receive a list of successfully evaluated models")
def and_check(context):
    """
    Ensure the check command with verbose ran returned the list of models.

    Args:
        context: Active context to check against.
    """
    assert ("was successful." in context.output_message)  # only appears when using verbose


@then("I should receive generated files in a temporary directory")
def gen_plugin_results(context):
    """
    Checks the output from the gen-plugin command.

    Args:
        context: Active context to check against.
    """
    src = os.path.join(context.src_dir, "aac_example/plugins/plugin_name")
    tests = os.path.join(context.test_dir, "test_aac_example/plugins/plugin_name")
    # make sure the files were created correctly
    assert (os.path.exists(os.path.join(src, "__init__.py")))
    assert (os.path.exists(os.path.join(src, "my_plugin_impl.py")))
    assert (os.path.exists(os.path.join(tests, "test_my_plugin.py")))
    assert (os.path.exists(os.path.join(tests, "my_plugin_success_test.feature")))
    assert (os.path.exists(os.path.join(tests, "my_plugin_failure_test.feature")))

    if os.path.exists(context.temp_dir):
        rmtree(context.temp_dir)
