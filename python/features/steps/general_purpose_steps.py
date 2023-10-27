from behave import given, when, then, use_step_matcher
import os
from aac.execute.command_line import cli, initialize_cli
from click.testing import CliRunner
from typing import Tuple

use_step_matcher("cfparse")

def get_model_file(context, path: str) -> str:
    return os.path.sep.join([context.config.paths[0], path])

def run_cli_command_with_args(command_name: str, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, [command_name] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

@given(u'I have the "{model_file}" model')
def given_model(context, model_file):
    model_path = get_model_file(context, model_file)
    if not os.path.exists(model_path):
        raise AssertionError(f"Model file {model_path} does not exist")


@when(u'I check the "{model_file}" model')
def check_model(context, model_file):
    exit_code, output_message = run_cli_command_with_args("check", [get_model_file(context, model_file)])
    if exit_code != 0:
        raise AssertionError(f"Check cli command failed with message: {output_message}")
    context.output_message = output_message


@then(u'I should receive a message that the check was successful')
def check_success(context):
    if "All AaC constraint checks were successful." not in context.output_message:
        raise AssertionError(f"Model check failed with message: {context.output_message}")
    