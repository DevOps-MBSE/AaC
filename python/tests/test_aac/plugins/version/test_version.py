from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.version.version_impl import plugin_name, version


class TestVersion(TestCase):

    def test_version(self):
        version_result = version()
        # make sure the command was successful
        self.assertEqual(version_result.status_code, ExecutionStatus.SUCCESS)

        # get the reported version string
        message = version_result.messages[0]

        # make sure the version conforms to semantic versioning
        version_values = message.message.split(".")
        self.assertEqual(len(version_values), 3, "Version should have 3 values separated by . to follow semantic versioning standards.")
        for value in version_values:
            self.assertTrue(value.isdigit(), f"Each token of the version should be a digit.  Received {value}")

    def run_version_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["version"] + args)
        exit_code = result.exit_code
        output_message = result.output.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_version(self):
        args = []

        exit_code, output_message = self.run_version_cli_command_with_args(args)

        self.assertEqual(0, exit_code)  # asserts the command ran successfully
        self.assertTrue(len(output_message) > 0)  # asserts the command produced output
        version_values = output_message.strip().split(".")
        self.assertEqual(len(version_values), 3, "Version should have 3 values separated by . to follow semantic versioning standards.")
        for value in version_values:
            self.assertTrue(value.isdigit(), f"Each token of the version should be a digit.  Received {value}")