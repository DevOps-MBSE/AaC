from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_error import LanguageError

import os
import shutil
import tempfile


from aac.plugins.check.check_aac_impl import plugin_name, check


class TestCheckAaC(TestCase):
    def test_check(self):
        # Let's just test via CLIf for now
        pass

    def run_check_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["check"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_check(self):
        """Test the CLI command for the check plugin."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "good.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

    def test_cli_check_bad_data(self):
        """Test the CLI command for the check plugin."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "bad.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]
            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            self.assertNotEqual(0, exit_code)
            self.assertIn("was expected to be list, but was", output_message)
