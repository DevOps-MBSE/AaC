from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.print_defs.print_aac_definitions_impl import plugin_name, print_defs


class TestPrintAaCDefinitions(TestCase):
    def test_print_defs(self):
        
        result1 = print_defs(False)
        self.assertTrue(result1.is_success(), f"Expected success but failed with message: {result1.is_success()}")
        self.assertTrue(len(result1.get_messages_as_string()) > 0, f"Expected at least one message but received none.")

        result2 = print_defs(True)
        self.assertTrue(result2.is_success(), f"Expected success but failed with message: {result2.is_success()}")
        self.assertTrue(len(result1.get_messages_as_string()) > 0, f"Expected at least one message but received none.")
        

    def run_print_defs_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["print-defs"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_print_defs(self):
        args = ["--core-only"]

        # TODO: populate args list, or pass empty list for no args

        exit_code, output_message = self.run_print_defs_cli_command_with_args(args)

        # TODO:  perform assertions against the output message
        self.assertEqual(0, exit_code)  # asserts the command ran successfully
        self.assertTrue(len(output_message) > 0)  # asserts the command produced output
        # TODO:  assert the output message is correct
