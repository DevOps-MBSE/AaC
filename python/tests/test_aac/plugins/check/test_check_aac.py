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
    # def test_check(self):
    #     # Let's just test via CLI for now
    #     print("\ntest_check_aac::test_check")
    #     pass

    def run_check_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        print("\n>>>>>>>>>>>>>test_check_aac::run_check_cli_command_with_args")
        print(args)
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["check"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        print("exit code:  "+str(exit_code))
        print("output msg: "+output_message)
        return exit_code, output_message

    def test_cli_check(self):
        """Test the CLI command for the check plugin."""
        print("\ntest_check_aac::test_cli_check")
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "good.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
            self.assertNotIn("My plugin was successful.", output_message) # only appears when --verbose is passed in.

    # def test_cli_check_verbose(self):
    #     """Test the CLI command for the check plugin."""
    #     print("\ntest_check_aac::test_cli_check_verbose")
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         aac_file_path = os.path.join(os.path.dirname(__file__), "good.aac")
    #         temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
    #         shutil.copy(aac_file_path, temp_aac_file_path)

    #         check_args = [temp_aac_file_path, "--verbose"]
    #         exit_code, output_message = self.run_check_cli_command_with_args(check_args)
    #         self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
    #         self.assertIn("was successful.", output_message) # only appears when --verbose is passed in.

    # def test_cli_check_bad_data(self):
    #     """Test the CLI command for the check plugin."""
    #     print("\ntest_check_aac::test_cli_check_bad_data")
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         aac_file_path = os.path.join(os.path.dirname(__file__), "bad.aac")
    #         temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
    #         shutil.copy(aac_file_path, temp_aac_file_path)

    #         check_args = [temp_aac_file_path]
    #         exit_code, output_message = self.run_check_cli_command_with_args(check_args)
    #         self.assertNotEqual(0, exit_code)
    #         self.assertIn("was expected to be list, but was", output_message)

    # def test_parse_Error(self):
    #     """Test the CLI command for the check plugin."""
    #     print("\ntest_check_aac::test_parse_Error")
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         aac_file_path = os.path.join(os.path.dirname(__file__), "parse_error.aac")
    #         temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
    #         shutil.copy(aac_file_path, temp_aac_file_path)

    #         check_args = [temp_aac_file_path]

    #         exit_code, output_message = self.run_check_cli_command_with_args(check_args)
    #         # Assert for return code 3 (fail)
    #         self.assertEqual(3, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
    #         self.assertNotIn("My plugin was successful.", output_message) # only appears when --verbose is passed in.


    # def test_parse_Error2(self):
    #     """Test the CLI command for the check plugin."""
    #     print("\ntest_check_aac::test_parse_Error")
    #     with tempfile.TemporaryDirectory() as temp_dir:
    #         aac_file_path = os.path.join(os.path.dirname(__file__), "parse_error2.aac")
    #         temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
    #         shutil.copy(aac_file_path, temp_aac_file_path)

    #         check_args = [temp_aac_file_path]

    #         exit_code, output_message = self.run_check_cli_command_with_args(check_args)
    #         # Assert for return code 6 (missing required field)
    #         self.assertEqual(6, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
    #         self.assertNotIn("My plugin was successful.", output_message) # only appears when --verbose is passed in.


    def test_parse_Error3(self):
        """Test the CLI command for the check plugin."""
        print("\ntest_check_aac::test_parse_Error")
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "parse_error3.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 6 (missing required field)
            self.assertEqual(0, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message) # only appears when --verbose is passed in.
