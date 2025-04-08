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
            package_doc_path = path.join(temp_dir, "docs")
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)

            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path,"--no-prompt"]

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
            self.assertTrue(path.exists(path.join(package_doc_path, "my_plugin.md")))

            # Ensure feature files were generated with a Given, When, and Then.
            files = listdir(package_tests_path)
            feature_files = list(filter(lambda x: ".feature" in x, files))
            for feature_file in feature_files:
                f = open(path.join(package_tests_path, feature_file), "r")
                file_content = f.read()
                self.assertIn("Given", file_content)
                self.assertIn("When", file_content)
                self.assertIn("Then", file_content)
                f.close()

            # Ensure the feature file steps were assigned to the correct keyword.
            file = open(path.join(package_tests_path, "my_plugin_command_test.feature"), "r")
            file_content = file.read()
            self.assertIn("Given An AaC file containing schemas with no extra fields.", file_content)
            self.assertIn("When The AaC check command is run on the schema.", file_content)
            self.assertIn("Then The check commands provides the output 'All AaC constraint checks were successful.'", file_content)
            file.close()


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
            package_doc_path = path.join(temp_dir, "docs")
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            file.close()
            # Check for documentation generation
            file = open(path.join(package_doc_path, "my_plugin.md"), "r")
            file_read = file.read()
            self.assertIn("test-command-one", file_read)
            self.assertNotIn("test-command-1-evaluation", file_read)
            file.close()
            # Confirm no generated .aac_backup files
            self.assertFalse(path.exists(path.join(package_src_path, "my_plugin_impl.py.aac_backup")))

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin_eval.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt",  "--force-overwrite"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_one(aac_plugin_file: str)", file_read)
            file.close()
            # Check for documentation generation
            file = open(path.join(package_doc_path, "my_plugin.md"), "r") # Note that the name stays as my_plugin because it comes from the name found within my_plugin_eval.aac
            file_read = file.read()
            self.assertIn("test-command-1-evaluation", file_read)
            self.assertNotIn("test-command-one", file_read)
            file.close()
            # Check for generated .aac_backup files
            self.assertTrue(path.exists(path.join(package_src_path, "my_plugin_impl.py.aac_backup")))

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
            package_doc_path = path.join(temp_dir, "docs")
            plugin_file_path = path.join(package_src_path, "my_plugin.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            self.assertNotIn("test_command_one_evaluation(aac_plugin_file: str)", file_read)
            file.close()
            # Confirm no generated .aac_evaluate files
            self.assertFalse(path.exists(path.join(package_src_path, "my_plugin_impl.py.aac_evaluate")))

            aac_plugin_path = path.join(path.dirname(__file__), "my_plugin_eval.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt", "--evaluate"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_src_path, "my_plugin_impl.py"), "r")
            file_read = file.read()
            self.assertNotIn("test_command_1_evaluation(aac_plugin_file: str)", file_read)
            self.assertIn("test_command_one(aac_plugin_file: str)", file_read)
            file.close()
            # Check for documentation generation
            file = open(path.join(package_doc_path, "my_plugin.md"), "r") # Note that the name stays as my_plugin because it comes from the name found within my_plugin_eval.aac
            file_read = file.read()
            self.assertIn("test-command-one", file_read)
            self.assertNotIn("test-command-1-evaluation", file_read)
            file.close()
            # Check .aac_evaluate file has been created
            self.assertTrue(path.exists(path.join(package_src_path, "my_plugin_impl.py.aac_evaluate")))

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

    # There is a special case where documentation needs to be generated for optional arguments
    # This tests for that special case and the expected hard-coded header of "Optional Arguments"
    # The other tests in this file account for the nominal cases
    def test_cli_gen_plugin_optional_args_documentation(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            # now create an AaC plugin file in the project src directory
            aac_file_path = path.join(path.dirname(__file__), "gen_plugin_optional_args.aac")
            temp_aac_file_path = path.join(temp_dir, "gen_plugin_optional_args.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]
            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_doc_path = path.join(temp_dir, "docs")
            plugin_file_path = path.join(package_src_path, "gen_plugin_optional_args.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "gen_plugin_optional_args.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_doc_path, "gen_plugin.md"), "r")
            file_read = file.read()
            self.assertIn("Optional Arguments", file_read) # Optional header to test for
            self.assertIn("--doc-output", file_read) # Optional argument from gen_plugin_optional_args.aac
            file.close()

    # There is a special case where documentation needs to be generated but the plugin has no arguments
    # This tests for that special case and the expected hard-coded language of "There are no arguments for the..."
    # The other tests in this file account for the nominal cases
    def test_cli_gen_plugin_no_args_documentation(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            # now create an AaC plugin file in the project src directory
            aac_file_path = path.join(path.dirname(__file__), "version_no_args.aac")
            temp_aac_file_path = path.join(temp_dir, "version_no_args.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]
            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            package_src_path = path.join(temp_dir, "src", "happy")
            mkdir(package_src_path)
            package_doc_path = path.join(temp_dir, "docs")
            plugin_file_path = path.join(package_src_path, "version_no_args.aac")

            aac_plugin_path = path.join(path.dirname(__file__), "version_no_args.aac")
            copy(aac_plugin_path, plugin_file_path)
            plugin_args = [plugin_file_path, "--code-output", path.join(temp_dir, "src"), "--test-output", path.join(temp_dir, "tests"), "--doc-output", package_doc_path, "--no-prompt"]
            exit_code, output_message = self.run_gen_plugin_cli_command_with_args(plugin_args)
            file = open(path.join(package_doc_path, "version.md"), "r")
            file_read = file.read()
            self.assertIn("There are no arguments for the", file_read)
            file.close()


    # Test input triggers a LanguageError
    # Value of 'parent_specs' was expected to be list, but was '<class 'str'>'
    # See src/tests/test_aac/plugins/check/test_check_aac.py test_cli_check_bad_data method for a sibling method
    def test_cli_gen_plugin_bad_data(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "bad.aac")
            temp_aac_file_path = path.join(temp_dir, "bad.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            self.assertEqual(6, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("Value of 'parent_specs' was expected to be list, but was", output_message)


    # Test input with an an invalid value
    # output msg: Invalid value for field 'name'.  Expected type 'str', but found '<class 'list'>'
    # See src/tests/test_aac/plugins/check/test_check_aac.py for a sibling method
    def test_cli_gen_plugin_invalid_value(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "invalid_value.aac")
            temp_aac_file_path = path.join(temp_dir, "invalid_value.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            # Assert for return code 1 (1 is the value for CONSTRAINT_FAILURE which is the status set upon receiving a LanguageError)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Invalid value for field 'name'.", output_message)


    # Test input missing required 'when' field primitive
    # output msg: Missing required field when.
    # See src/tests/test_aac/plugins/check/test_check_aac.py for a sibling method
    def test_cli_gen_plugin_missing_required_field(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "missing_required_field.aac")
            temp_aac_file_path = path.join(temp_dir, "missing_required_field.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            # Assert for return code 1 (1 is the value for CONSTRAINT_FAILURE which is the status set upon receiving a LanguageError)
            self.assertEqual(1, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("LanguageError from parse_and_load: Missing required field", output_message)


    # Test input improper YAML
    # output msg: The AaC file '/tmp/{random-temp-name}/my_plugin.aac' could not be parsed.
    # See src/tests/test_aac/plugins/check/test_check_aac.py for a sibling method
    def test_cli_gen_plugin_parse_error(self):
        # first we need a project to work in, so generate a temporary one
        with TemporaryDirectory() as temp_dir:
            aac_file_path = path.join(path.dirname(__file__), "parse_error.aac")
            temp_aac_file_path = path.join(temp_dir, "parse_error.aac")
            copy(aac_file_path, temp_aac_file_path)

            proj_args = [temp_aac_file_path, "--output", temp_dir, "--no-prompt"]

            exit_code, output_message = self.run_gen_project_cli_command_with_args(proj_args)

            # Assert for return code 3 (3 is the value for PARSER_FAILURE which is the status set upon receiving a ParserError)
            self.assertEqual(3, exit_code, f"Expected to fail but ran successfully with message: {output_message}")
            self.assertNotIn("My plugin was successful.", output_message)  # only appears when --verbose is passed in.
            self.assertIn("ParserError from parse_and_load. Encountered an invalid YAML", output_message)
