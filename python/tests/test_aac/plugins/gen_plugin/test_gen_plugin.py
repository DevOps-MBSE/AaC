from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus

import os
import shutil
import tempfile

import traceback

from aac.plugins.gen_plugin.gen_plugin_impl import (
    plugin_name,
    gen_plugin,
    before_gen_plugin_check,
    after_gen_plugin_generate,
    gen_project,
    before_gen_project_check,
    after_gen_project_generate,
)


class TestGenPlugin(TestCase):

    def test_gen_plugin(self):
        # I'm going to rely on the CLI testing for this one, but will leave there here in case we need it later
        pass

    def run_gen_plugin_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["gen-plugin"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_gen_plugin(self):
        # first we need a project to work in, so generate a temporary one
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_project.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = os.path.join(temp_dir, "src", "happy")
            os.mkdir(package_src_path)
            package_tests_path = os.path.join(temp_dir, "tests", "test_happy")
            os.mkdir(package_tests_path)
            plugin_file_path = os.path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = os.path.join(os.path.dirname(__file__), "my_plugin.aac")
            shutil.copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", os.path.join(temp_dir, "src"), "--test-output", os.path.join(temp_dir, "tests"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            # make sure the files were created correctly
            self.assertTrue(os.path.exists(os.path.join(package_src_path, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(package_src_path, "my_plugin_impl.py")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "test_my_plugin.py")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_context_test.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_schema_test.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_primitive_test.feature")))

    def test_cli_gen_plugin_with_incomplete_dirs(self):
        # first we need a project to work in, so generate a temporary one
         with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_project.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = os.path.join(temp_dir, "src", "happy")
            os.mkdir(package_src_path)
            plugin_file_path = os.path.join(temp_dir, "my_plugin.aac")

            aac_plugin_path = os.path.join(os.path.dirname(__file__), "my_plugin.aac")
            shutil.copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", os.path.join(temp_dir, "src"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            self.assertTrue(os.path.exists(os.path.join(package_src_path, "my_plugin_impl.py")))

            package_tests_path = os.path.join(temp_dir, "test_happy") # making sure that tests get output to the correct location
            self.assertTrue(os.path.exists(os.path.join(package_src_path, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test_two.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test_three.feature")))

    def test_cli_gen_plugin_multiple_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_project.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = os.path.join(temp_dir, "src", "happy")
            os.mkdir(package_src_path)
            package_tests_path = os.path.join(temp_dir, "tests", "test_happy")
            os.mkdir(package_tests_path)
            plugin_file_path = os.path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = os.path.join(os.path.dirname(__file__), "my_plugin.aac")
            shutil.copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", os.path.join(temp_dir, "src"), "--test-output", os.path.join(temp_dir, "tests"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            self.assertTrue(os.path.exists(os.path.join(package_src_path, "my_plugin_impl.py")))
            with open(os.path.join(package_src_path, "my_plugin_impl.py")) as impl_file:
                impl_file_read = impl_file.read()
                self.assertIn("def before_test_command_one_check", impl_file_read)
                self.assertIn("def test_command_one", impl_file_read)
                self.assertIn("def after_test_command_one_generate", impl_file_read)

                self.assertIn("def before_test_command_two_check", impl_file_read)
                self.assertIn("def test_command_two", impl_file_read)
                self.assertIn("def after_test_command_two_generate", impl_file_read)

                self.assertIn("def before_test_command_three_check", impl_file_read)
                self.assertIn("def test_command_three", impl_file_read)
                self.assertIn("def after_test_command_three_generate", impl_file_read)

            self.assertTrue(os.path.exists(os.path.join(package_src_path, "__init__.py")))
            with open(os.path.join(package_src_path, "__init__.py")) as init_file:
                init_file_read = init_file.read()
                self.assertIn("def run_test_command_one", init_file_read)

                self.assertIn("def run_test_command_two", init_file_read)

                self.assertIn("def run_test_command_three", init_file_read)
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test_two.feature")))
            self.assertTrue(os.path.exists(os.path.join(package_tests_path, "my_plugin_command_test_three.feature")))


    def test_gen_project(self):
        # I'm going to rely on the CLI testing for this one, but will leave there here in case we need it later
        pass

    def run_gen_project_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["gen-project"] + args)
        if result.exception:
            exc_type, exc_value, exc_traceback = result.exc_info
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_gen_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_project.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            # make sure the files and directories were created
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "pyproject.toml")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "tox.ini")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "README.md")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "src")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "tests")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "docs")))
