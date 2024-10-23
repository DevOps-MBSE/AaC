from io import StringIO
from unittest import TestCase
from unittest.mock import patch
from typing import Tuple
from click.testing import CliRunner
from os import path, mkdir, listdir
from shutil import copy
from tempfile import TemporaryDirectory
from traceback import print_exception

from aac.execute.command_line import cli, initialize_cli


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
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_tests_path = path.join(temp_dir, "tests", "test_happy")
            mkdir(package_tests_path)
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            # make sure the files were created correctly
            self.assertTrue(path.exists(path.join(package_src_path, "__init__.py")))
            self.assertTrue(path.exists(path.join(package_src_path, "my_plugin_impl.py")))
            self.assertTrue(path.exists(path.join(package_tests_path, "test_my_plugin.py")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_context_test.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_schema_test.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_primitive_test.feature")))

    def test_cli_gen_plugin_overwrite(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            # now create an AaC plugin file in the project src directory
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]
            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_tests_path = path.join(temp_dir, "tests", "test_happy")
            mkdir(package_tests_path)
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            file.close()

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin_eval.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt", "--force-overwrite"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_one(aac_plugin_file: str)", file_read)
            file.close()


    def test_cli_gen_plugin_evaluate(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            # now create an AaC plugin file in the project src directory
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]
            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_tests_path = path.join(temp_dir, "tests", "test_happy")
            mkdir(package_tests_path)
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_one_evaluation(aac_plugin_file: str)", file_read)
            file.close()

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin_eval.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt", "--evaluate"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertNotIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            file.close()


    def test_cli_gen_plugin_with_incomplete_dirs(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            plugin_file_path = path.join(temp_dir, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            self.assertTrue(path.exists(path.join(package_src_path, "my_plugin_impl.py")))

            package_tests_path = path.join(temp_dir, "test_happy")  # making sure that tests get output to the correct location
            self.assertTrue(path.exists(path.join(package_src_path, "__init__.py")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test_two.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test_three.feature")))

    def test_cli_gen_plugin_multiple_commands(self):
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

            # now create an AaC plugin file in the project src directory
            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_tests_path = path.join(temp_dir, "tests", "test_happy")
            mkdir(package_tests_path)
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            self.assertEqual(0, exit_code)  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            self.assertTrue(path.exists(path.join(package_src_path, "my_plugin_impl.py")))
            with open(path.join(package_src_path, "my_plugin_impl.py")) as impl_file:
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

            self.assertTrue(path.exists(path.join(package_src_path, "__init__.py")))
            with open(path.join(package_src_path, "__init__.py")) as init_file:
                init_file_read = init_file.read()
                self.assertIn("def run_test_command_one", init_file_read)

                self.assertIn("def run_test_command_two", init_file_read)

                self.assertIn("def run_test_command_three", init_file_read)
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test_two.feature")))
            self.assertTrue(path.exists(path.join(package_tests_path, "my_plugin_command_test_three.feature")))

    # The following decorators are to stop std_out and std_err from clogging up the terminal with System errors.
    @patch('sys.stdout', new_callable=StringIO)  # Suppress stdout
    @patch('sys.stderr', new_callable=StringIO)  # Suppress stderr
    def test_cli_gen_plugin_failure(self, mock_stderr, mock_stdout):
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_plugin_bad.aac")
            temp_aac_file_path = path.join(temp_dir, "my_plugin_bad.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--code-output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(proj_args)
            self.assertNotEqual(0, exit_code)
            self.assertIn("Definition is missing field 'name'", output_message)

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
            print_exception(exc_type, exc_value, exc_traceback)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    def test_cli_gen_project(self):
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_project.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project.aac")
            copy(aac_file_path, temp_aac_file_path)

            args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(args)

            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully
            self.assertIn("All AaC constraint checks were successful", output_message)  # asserts the command ran check successfully

            # make sure the files and directories were created
            self.assertTrue(path.exists(path.join(temp_dir, "pyproject.toml")))
            self.assertTrue(path.exists(path.join(temp_dir, "tox.ini")))
            self.assertTrue(path.exists(path.join(temp_dir, "README.md")))
            self.assertTrue(path.exists(path.join(temp_dir, "src")))
            self.assertTrue(path.exists(path.join(temp_dir, "tests")))
            self.assertTrue(path.exists(path.join(temp_dir, "docs")))

    # The following decorators are to stop std_out and std_err from clogging up the terminal with System errors.
    @patch('sys.stdout', new_callable=StringIO)  # Suppress stdout
    @patch('sys.stderr', new_callable=StringIO)  # Suppress stderr
    def test_cli_gen_project_failure(self, mock_stderr, mock_stdout):
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "my_project_bad.aac")
            temp_aac_file_path = path.join(temp_dir, "my_project_bad.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)
            self.assertNotEqual(0, exit_code)
            self.assertIn("Definition is missing field 'name'", output_message)
