import os

from tempfile import TemporaryDirectory
from typing import Optional
from unittest.mock import patch

from aac.io.constants import YAML_DOCUMENT_EXTENSION, YAML_DOCUMENT_SEPARATOR
from aac.plugins.contributions.contribution_types.definition_validation_contribution import DefinitionValidationContribution
from aac.plugins.first_party.gen_plugin.GeneratePluginException import GeneratePluginException
from aac.plugins.first_party.gen_plugin.gen_plugin_impl import (
    EXPECTED_FIRST_PARTY_DIRECTORY_PATH,
    PLUGIN_TYPE_THIRD_STRING,
    _collect_all_plugin_definitions,
    _convert_template_name_to_file_name,
    _get_repository_root_directory_from_path,
    _prepare_and_generate_plugin_files,
    generate_plugin,
)
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.validate import validated_source

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_failure, assert_plugin_success
from tests.helpers.io2.TemporaryTestFile import TemporaryTestFile
from tests.helpers.io2.directory import new_working_dir


INIT_TEMPLATE_NAME = "__init__.py.jinja2"
PLUGIN_IMPL_TEMPLATE_NAME = "plugin_impl.py.jinja2"
PLUGIN_IMPL_TEST_TEMPLATE_NAME = "test_plugin_impl.py.jinja2"
SETUP_TEMPLATE_NAME = "setup.py.jinja2"
README_TEMPLATE_NAME = "README.md.jinja2"
TOX_CONFIG_TEMPLATE_NAME = "tox.ini.jinja2"


class TestGenPlugin(ActiveContextTestCase):
    @patch("aac.validate._collect_validators._get_validator_plugin_by_name")
    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_first_party_plugin(self, is_user_desired_output_dir, get_validator_plugin_by_name):
        is_user_desired_output_dir.return_value = True
        get_validator_plugin_by_name.side_effect = _ignore_missing_validator_implementations_error_for_test_validations

        with TemporaryDirectory() as tmpdir:
            self.assertEqual(len(os.listdir(tmpdir)), 0)

            plugin_dir = os.path.join(tmpdir, EXPECTED_FIRST_PARTY_DIRECTORY_PATH, "plugin")
            os.makedirs(plugin_dir)

            # Write the plugin file into the "fake" test repo path
            with (
                new_working_dir(plugin_dir),
                TemporaryTestFile(TEST_PLUGIN_YAML_STRING, dir=plugin_dir) as test_file,
                TemporaryTestFile(TEST_PLUGIN_DEFINITIONS_YAML_STRING, dir=plugin_dir, name=TEST_PLUGIN_DEFINITIONS_FILE_NAME),
            ):
                result = generate_plugin(test_file.name)
                assert_plugin_success(result)

                # Assert that top-level are all directories, no files at the top should be generated
                self.assertEqual(len(os.listdir(tmpdir)), 2)

                # Assert the test was generated
                generated_test_file = os.listdir(f"{tmpdir}/tests/plugins/")
                self.assertEqual(len(generated_test_file), 1)
                self.assertIn(f"test_{TEST_PLUGIN_NAME}_impl.py", generated_test_file)

                # Assert the plugin was generated
                generated_plugin_files = os.listdir(plugin_dir)
                self.assertEqual(len(generated_plugin_files), 4)
                self.assertIn("__init__.py", generated_plugin_files)
                self.assertIn(f"{TEST_PLUGIN_NAME}_impl.py", generated_plugin_files)
                self.assertIn(os.path.basename(test_file.name), generated_plugin_files)

    @patch("aac.validate._collect_validators._get_validator_plugin_by_name")
    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_third_party_plugin(self, is_user_desired_output_dir, get_validator_plugin_by_name):
        is_user_desired_output_dir.return_value = True
        get_validator_plugin_by_name.side_effect = _ignore_missing_validator_implementations_error_for_test_validations

        with (
            TemporaryDirectory() as tmpdir,
            new_working_dir(tmpdir),
            TemporaryTestFile(TEST_PLUGIN_YAML_STRING, dir=tmpdir) as test_file,
            TemporaryTestFile(TEST_PLUGIN_DEFINITIONS_YAML_STRING, dir=tmpdir, name=TEST_PLUGIN_DEFINITIONS_FILE_NAME),
        ):
            self.assertEqual(len(os.listdir(tmpdir)), 2)

            result = generate_plugin(test_file.name)
            assert_plugin_success(result)

            generated_plugin_files = [os.path.join(root, file) for root, _, files in os.walk(tmpdir) for file in files]
            self.assertEqual(len(generated_plugin_files), 8)
            self.assertEqual(len([file for file in generated_plugin_files if os.path.basename(test_file.name) in file]), 1)
            self.assertGreater(len([file for file in generated_plugin_files if TEST_PLUGIN_NAME in file]), 0)

    @patch("aac.validate._collect_validators._get_validator_plugin_by_name")
    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_plugin_fails_with_multiple_plugins(self, is_user_desired_output_dir, get_validator_plugin_by_name):
        is_user_desired_output_dir.return_value = True
        get_validator_plugin_by_name.side_effect = _ignore_missing_validator_implementations_error_for_test_validations

        with (
            TemporaryDirectory() as tmpdir,
            new_working_dir(tmpdir),
            TemporaryTestFile(f"{TEST_PLUGIN_YAML_STRING}\n---\n{SECONDARY_PLUGIN_YAML_STRING}", dir=tmpdir) as test_file,
            TemporaryTestFile(TEST_PLUGIN_DEFINITIONS_YAML_STRING, dir=tmpdir, name=TEST_PLUGIN_DEFINITIONS_FILE_NAME),
        ):
            result = generate_plugin(test_file.name)

            temp_directory_files = os.listdir(tmpdir)
            assert_plugin_failure(result)
            self.assertEqual(len(temp_directory_files), 2)
            self.assertIn(os.path.basename(test_file.name), temp_directory_files)

    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_plugin_returns_op_cancelled_when_confirmation_is_false(self, is_user_desired_output_dir):
        is_user_desired_output_dir.return_value = False

        with TemporaryDirectory() as temp_directory:
            self.assertEqual(len(os.listdir(temp_directory)), 0)

            with TemporaryTestFile(TEST_PLUGIN_YAML_STRING, dir=temp_directory) as plugin_yaml:
                result = generate_plugin(plugin_yaml.name)

                temp_directory_files = os.listdir(temp_directory)
                self.assertEqual(result.status_code, PluginExecutionStatusCode.OPERATION_CANCELLED)
                self.assertEqual(len(temp_directory_files), 1)
                self.assertIn(os.path.basename(plugin_yaml.name), temp_directory_files)

    def test_convert_template_name_to_file_name(self):
        plugin_name = "aac-test"
        template_names = [
            INIT_TEMPLATE_NAME,
            PLUGIN_IMPL_TEMPLATE_NAME,
            SETUP_TEMPLATE_NAME,
        ]
        expected_filenames = [
            "__init__.py",
            f"{plugin_name}_impl.py",
            "setup.py",
        ]

        for i in range(len(template_names)):
            expected_filename = expected_filenames[i]
            actual_filename = _convert_template_name_to_file_name(template_names[i], plugin_name)
            self.assertEqual(expected_filename, actual_filename)

    def test_prepare_and_generate_plugin_files(self):
        with (
            TemporaryDirectory() as tmpdir,
            new_working_dir(tmpdir),
            TemporaryTestFile(TEST_PLUGIN_YAML_STRING, dir=tmpdir) as test_file,
            TemporaryTestFile(TEST_PLUGIN_DEFINITIONS_YAML_STRING, dir=tmpdir, name=TEST_PLUGIN_DEFINITIONS_FILE_NAME),
        ):
            generated_templates = _prepare_and_generate_plugin_files(
                _collect_all_plugin_definitions(test_file.name), PLUGIN_TYPE_THIRD_STRING, test_file.name, tmpdir
            )

            generated_template_names = []
            generated_template_output_directories = []
            for template in generated_templates.values():
                generated_template_names.append(template.file_name)
                generated_template_output_directories.append(os.path.basename(template.output_directory))

        # Check that the files don't have "-" in the name
        for name in generated_template_names:
            self.assertNotIn("-", name)

        # Check that the expected files and directories were created and named correctly
        num_generated_templates = len(generated_templates)
        self.assertEqual(len(generated_template_names), num_generated_templates)
        self.assertEqual(len(generated_template_output_directories), num_generated_templates)

        # Assert that the expected template files were generated
        self.assertIn("README.md", generated_template_names)
        self.assertIn("tox.ini", generated_template_names)
        self.assertIn("__init__.py", generated_template_names)
        self.assertIn("setup.py", generated_template_names)
        self.assertIn(f"{TEST_PLUGIN_NAME}_impl.py", generated_template_names)
        self.assertIn(f"test_{TEST_PLUGIN_NAME}_impl.py", generated_template_names)

        self.assertIn("tests", generated_template_output_directories)

        # Assert that some expected content is present
        generated_plugin_file_contents = generated_templates.get(INIT_TEMPLATE_NAME).content
        self.assertIn("@hookimpl", generated_plugin_file_contents)
        self.assertIn("get_plugin", generated_plugin_file_contents)
        self.assertIn("test_plugin_command_arguments", generated_plugin_file_contents)
        self.assertIn("import plugin_name, test_plugin_command", generated_plugin_file_contents)
        self.assertIn("architecture_file", generated_plugin_file_contents)

        generated_plugin_impl_file_contents = generated_templates.get(PLUGIN_IMPL_TEMPLATE_NAME).content
        self.assertIn("def test_plugin_command", generated_plugin_impl_file_contents)
        self.assertIn("architecture_file (str)", generated_plugin_impl_file_contents)
        self.assertIn("with plugin_result", generated_plugin_impl_file_contents)
        self.assertIn("return result", generated_plugin_impl_file_contents)

        generated_plugin_impl_test_file_contents = generated_templates.get(PLUGIN_IMPL_TEST_TEMPLATE_NAME).content
        self.assertIn("TestTestPlugin(TestCase)", generated_plugin_impl_test_file_contents)

        generated_readme_file_contents = generated_templates.get(README_TEMPLATE_NAME).content
        self.assertIn("# Test Plugin", generated_readme_file_contents)
        self.assertIn("## Command:", generated_readme_file_contents)
        self.assertIn("$ aac test-plugin-command", generated_readme_file_contents)
        self.assertIn("## Plugin Extensions and Definitions", generated_readme_file_contents)
        self.assertIn("### Schema - TestPluginData", generated_readme_file_contents)
        self.assertIn("### Validation - Test definition validation", generated_readme_file_contents)
        self.assertIn("### Validation - Test primitive validation", generated_readme_file_contents)

        generated_tox_config_file_contents = generated_templates.get(TOX_CONFIG_TEMPLATE_NAME).content
        self.assertIn("[testenv]", generated_tox_config_file_contents)
        self.assertIn("[flake8]", generated_tox_config_file_contents)
        self.assertIn("[unittest]", generated_tox_config_file_contents)
        self.assertIn("[run]", generated_tox_config_file_contents)
        self.assertIn("[report]", generated_tox_config_file_contents)
        self.assertIn("code-directories = test_plugin", generated_tox_config_file_contents)
        self.assertIn("coverage = test_plugin", generated_tox_config_file_contents)
        self.assertIn("fail_under = 80.00", generated_tox_config_file_contents)

    def test__prepare_and_generate_plugin_files_errors_on_multiple_plugins(self):
        content = f"{SECONDARY_PLUGIN_YAML_STRING}\n{YAML_DOCUMENT_SEPARATOR}\n{TERTIARY_PLUGIN_YAML_STRING}"
        with validated_source(content) as result:
            self.assertRaises(
                GeneratePluginException,
                _prepare_and_generate_plugin_files,
                result.definitions,
                PLUGIN_TYPE_THIRD_STRING,
                "",
                "",
            )

    def test__get_repository_root_directory_from_path(self):
        path = "/workspace/AaC/python/src/aac/plugins/new_plugin"

        expected_result = "/workspace/AaC/python/"
        actual_result = _get_repository_root_directory_from_path(path)

        self.assertEqual(expected_result, actual_result)


def _ignore_missing_validator_implementations_error_for_test_validations(
    validator_name: str, validator_plugins: list[DefinitionValidationContribution]
) -> Optional[DefinitionValidationContribution]:
    """Don't require test validation plugins to have implementations."""

    from aac.plugins.validators.validator_implementation._validate_validator_implementation import VALIDATION_NAME

    plugins = [plugin for plugin in validator_plugins if validator_name != VALIDATION_NAME and plugin.name == validator_name]
    return plugins[0] if len(plugins) == 1 else None


TEST_PLUGIN_NAME = "test_plugin"
TEST_PLUGIN_DEFINITIONS_FILE_NAME = f"definitions{YAML_DOCUMENT_EXTENSION}"

TEST_PLUGIN_YAML_STRING = f"""
plugin:
  name: Test Plugin
  description: |
    A test plugin with a contributed definition, a command, a definition
    validation, and a primitive validation.
  definitionSources:
    - ./{TEST_PLUGIN_DEFINITIONS_FILE_NAME}
  definitionValidations:
    - name: Test definition validation
  primitiveValidations:
    - name: Test primitive validation
  commands:
    - name: test-plugin-command
      group: Internal
      display: do-thing
      helpText: Test plugin generation
      input:
        - name: architecture_file
          type: file
          python_type: str
          description: An architecture-as-code file.
      acceptance:
        - scenario: Test some stuff
          given:
            - The definitions in {{test-plugin-command.input.architecture_file}} represent a valid system architecture.
          when:
            - The command is run with the expected arguments.
          then:
            - Stuff happens
---
schema:
  name: TestPluginData
  fields:
    - name: value1
      type: string
    - name: value2
      type: string
  validation:
    - name: Required fields are present
      arguments:
        - value1
"""

TEST_PLUGIN_DEFINITIONS_YAML_STRING = """
validation:
  name: Test definition validation
  description: A test definition validator.
  behavior:
    - name: Validate a definition
      type: request-response
      input:
        - name: input
          type: ValidatorInput
      output:
        - name: results
          type: ValidatorOutput
      acceptance:
        - scenario: Successfully validate the definition
          given:
            - The ValidatorInput content consists of valid AaC definitions.
          when:
            - The validator plugin is executed.
          then:
            - The ValidatorOutput does not indicate any errors.
            - The ValidatorOutput does not indicate any warnings.
            - The ValidatorOutput indicates the validator plugin under test is valid.
---
validation:
  name: Test primitive validation
  description: A test primitive validator.
  behavior:
    - name: Validate a primitive
      type: request-response
      input:
        - name: input
          type: ValidatorInput
      output:
        - name: results
          type: ValidatorOutput
      acceptance:
        - scenario: Successfully validate the primitive
          given:
            - The ValidatorInput content consists of a valid primitive value.
          when:
            - The validator plugin is executed.
          then:
            - The ValidatorOutput does not indicate any errors.
            - The ValidatorOutput does not indicate any warnings.
            - The ValidatorOutput indicates the validator plugin under test is valid.
"""

SECONDARY_PLUGIN_YAML_STRING = """
plugin:
  name: Secondary Plugin
  description: An AaC plugin that does something else.
  commands:
    - name: secondary-plugin-command
      helpText: Do something else
      input:
        - name: architecture_file
          type: file
          python_type: str
          description: An architecture-as-code file.
      output:
        - name: structure
          type: Map
          python_type: dict
          description: A definition structure.
      acceptance:
        - scenario: Do some stuff
          given:
            - The {{secondary-plugin-command.input.architecture_file}} contains a valid architecture specification.
          when:
            - The aac app is run with the secondary-plugin-command command.
          then:
            - Some stuff will be done
"""

TERTIARY_PLUGIN_YAML_STRING = """
plugin:
  name: Tertiary Plugin
  description: Another AaC plugin that does something else.
  commands:
    - name: tertiary-plugin-command
      helpText: Do more things
      input:
        - name: architecture_file
          type: file
          python_type: str
          description: An architecture-as-code file.
      acceptance:
        - scenario: Do more things
          given:
            - The {{tertiary-plugin-command.input.architecture_file}} contains a valid architecture specification.
          when:
            - The aac app is run with the tertiary-plugin-command command.
          then:
            - Some stuff will be done
"""
