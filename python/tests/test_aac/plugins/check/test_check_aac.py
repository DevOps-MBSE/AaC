"""The AaC Check AaC plugin test module."""
from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
import os
import shutil
import tempfile


class TestCheckAaC(TestCase):
    """Class to test the Check AaC plugin."""

    # some default test
    def test_check(self):
        """Incomplete test method to directly test 'check'."""
        # Let's just test via CLI for now
        pass

    # The test helper method in this class which invokes the CliRunner for all of the other tests
    def run_check_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["check"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    # Happy path test without verbose flag
    # Test input passes all tests in parsing and check_aac_impl.py
    def test_cli_check(self):
        """Test the CLI command for the check plugin."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "good.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("my_plugin.aac", output_message)

    # Happy path test with verbose flag
    # Test input passes all tests in parsing and check_aac_impl.py
    def test_cli_check_verbose(self):
        """Test the CLI command for the check plugin with the verbose flag on."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "good.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path, "--verbose"]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
            self.assertIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("my_plugin.aac", output_message)

    # Test input triggers a LanguageError in check_aac_impl.py ~line 171
    # Value of 'parent_specs' was expected to be list, but was '<class 'str'>'
    def test_cli_check_bad_data(self):
        """Test check_aac_impl.py and trigger a LanguageError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "bad.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            self.assertNotEqual(0, exit_code)
            self.assertIn("was expected to be list, but was", output_message)
            self.assertIn("my_plugin.aac", output_message)

    # Test input improper YAML
    # output msg: The AaC file '/tmp/{random-temp-name}/my_plugin.aac' could not be parsed.
    def test_parse_Error(self):
        """Test check_aac_impl.py with improper YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "parse_error.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 3 (3 is the value for PARSER_FAILURE which is the status set upon receiving a ParserError)
            self.assertEqual(3, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("Encountered an invalid YAML with the following scanner error", output_message)

    # Test input missing required 'when' field primitive
    # output msg: Missing required field when.
    def test_unexpected_primitive(self):
        """Test check_aac_impl.py with a missing required field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "missing_required_field.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 1 (1 is the value for CONSTRAINT_FAILURE which is the status set upon receiving a LanguageError)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Missing required field when.", output_message)

    # Test input with an unknown primitive "stranger" which triggers a ParserError
    # output msg: Found undefined field name 'stranger' when expecting ['name', 'tags', 'requirements', 'given', 'when', 'then', 'examples'] as defined in Scenario
    def test_unknown_primitive(self):
        """Test check_aac_impl.py with an unknown primitive resulting in a ParserError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "unknown_field.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 1 (1 is the value for CONSTRAINT_FAILURE which is the status set upon receiving a LanguageError)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Found undefined field name 'stranger'", output_message)

    # Test input with an an invalid value
    # output msg: Invalid value for field 'name'.  Expected type 'str', but found '<class 'list'>'
    def test_invalid_value(self):
        """Test check_aac_impl.py with an invalid value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "invalid_value.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 1 (invalid value)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Invalid value for field 'name'", output_message)

    # Test input with an an undefined field name "whatzit"
    # output msg: Found undefined field name 'whatzit' when expecting ['name', 'description', 'sections', 'parent_specs', 'child_specs', 'requirements'] as defined in RequirementSpecification
    def test_undefined_field_name(self):
        """Test check_aac_impl.py with an undefined field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "undefined_field_name.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            check_args = [temp_aac_file_path]

            exit_code, output_message = self.run_check_cli_command_with_args(check_args)
            # Assert for return code 1 (1 is the value for CONSTRAINT_FAILURE which is the status set upon receiving a LanguageError)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Found undefined field name 'whatzit'", output_message)
