import os
from tempfile import TemporaryDirectory
from unittest.mock import patch

from aac.plugins.first_party.gen_plugin.gen_plugin_impl import (
    _prepare_and_generate_plugin_files,
    _convert_template_name_to_file_name,
    _get_repository_root_directory_from_path,
    generate_plugin,
)
from aac.plugins.first_party.gen_plugin.GeneratePluginException import GeneratePluginException
from aac.plugins.first_party.gen_plugin.gen_plugin_impl import EXPECTED_FIRST_PARTY_DIRECTORY_PATH, PLUGIN_TYPE_THIRD_STRING
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.validate import validated_source

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_failure, assert_plugin_success
from tests.helpers.io import temporary_test_file, temporary_test_file_wo_cm

INIT_TEMPLATE_NAME = "__init__.py.jinja2"
PLUGIN_IMPL_TEMPLATE_NAME = "plugin_impl.py.jinja2"
PLUGIN_IMPL_TEST_TEMPLATE_NAME = "test_plugin_impl.py.jinja2"
SETUP_TEMPLATE_NAME = "setup.py.jinja2"
README_TEMPLATE_NAME = "README.md.jinja2"
TOX_CONFIG_TEMPLATE_NAME = "tox.ini.jinja2"


class TestGenPlugin(ActiveContextTestCase):
    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_first_party_plugin(self, is_user_desired_output_dir):
        with TemporaryDirectory() as temp_directory:

            self.assertEqual(len(os.listdir(temp_directory)), 0)

            plugin_aac_path = os.path.join(temp_directory, EXPECTED_FIRST_PARTY_DIRECTORY_PATH, "test")
            os.makedirs(plugin_aac_path)

            # Write the plugin file into the "fake" test repo path
            with temporary_test_file(TEST_PLUGIN_YAML_STRING, dir=plugin_aac_path, suffix=".yaml") as plugin_yaml:
                is_user_desired_output_dir.return_value = True
                result = generate_plugin(plugin_yaml.name)

                assert_plugin_success(result)

                # Assert that top-level are all directories, no files at the top should be generated
                self.assertEqual(len(os.listdir(temp_directory)), 2)

                # Assert the test was generated
                generated_test_file = os.listdir(f"{temp_directory}/tests/plugins/")
                self.assertEqual(len(generated_test_file), 1)
                self.assertIn(f"test_{TEST_PLUGIN_NAME}_impl.py", generated_test_file)

                # Assert the plugin was generated
                generated_plugin_files = os.listdir(f"{temp_directory}/src/aac/plugins/test/")
                self.assertEqual(len(generated_plugin_files), 3)
                self.assertIn("__init__.py", generated_plugin_files)
                self.assertIn(f"{TEST_PLUGIN_NAME}_impl.py", generated_plugin_files)
                self.assertIn(os.path.basename(plugin_yaml.name), generated_plugin_files)

    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_third_party_plugin(self, is_user_desired_output_dir):

        with TemporaryDirectory() as temp_directory:
            temp_file = temporary_test_file_wo_cm(TEST_PLUGIN_YAML_STRING, dir=temp_directory, suffix=".yaml")

            is_user_desired_output_dir.return_value = True
            result = generate_plugin(temp_file.name)

            assert_plugin_success(result)

            generated_plugin_files = [os.path.join(root, file) for root, _, files in os.walk(temp_directory) for file in files]
            self.assertEqual(len(generated_plugin_files), 7)
            self.assertEqual(len([file for file in generated_plugin_files if os.path.basename(temp_file.name) in file]), 1)
            self.assertGreater(len([file for file in generated_plugin_files if TEST_PLUGIN_NAME in file]), 0)

    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_plugin_fails_with_multiple_models(self, is_user_desired_output_dir):
        with TemporaryDirectory() as temp_directory:

            self.assertEqual(len(os.listdir(temp_directory)), 0)

            content = f"{TEST_PLUGIN_YAML_STRING}\n---\n{SECONDARY_MODEL_YAML_DEFINITION}"
            with temporary_test_file(content, dir=temp_directory) as plugin_yaml:
                is_user_desired_output_dir.return_value = True
                result = generate_plugin(plugin_yaml.name)

                temp_directory_files = os.listdir(temp_directory)
                assert_plugin_failure(result)
                self.assertEqual(len(temp_directory_files), 1)
                self.assertIn(os.path.basename(plugin_yaml.name), temp_directory_files)

    @patch("aac.plugins.first_party.gen_plugin.gen_plugin_impl._is_user_desired_output_directory")
    def test_generate_plugin_returns_op_cancelled_when_confirmation_is_false(self, is_user_desired_output_dir):
        with TemporaryDirectory() as temp_directory:

            self.assertEqual(len(os.listdir(temp_directory)), 0)

            with temporary_test_file(TEST_PLUGIN_YAML_STRING, dir=temp_directory) as plugin_yaml:
                is_user_desired_output_dir.return_value = False
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
        with TemporaryDirectory() as temp_directory:
            temp_file = temporary_test_file_wo_cm(TEST_PLUGIN_YAML_STRING, dir=temp_directory, suffix=".yaml")

            with validated_source(temp_file.name) as result:
                plugin_name = "aac_gen_protobuf"

                generated_templates = _prepare_and_generate_plugin_files(
                    result.definitions, PLUGIN_TYPE_THIRD_STRING, temp_file.name, temp_directory
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
            self.assertIn(f"{plugin_name}_impl.py", generated_template_names)
            self.assertIn(f"test_{plugin_name}_impl.py", generated_template_names)

            self.assertIn("tests", generated_template_output_directories)

            # Assert that some expected content is present
            generated_plugin_file_contents = generated_templates.get(INIT_TEMPLATE_NAME).content
            self.assertIn("@hookimpl", generated_plugin_file_contents)
            self.assertIn("get_plugin", generated_plugin_file_contents)
            self.assertIn("gen_protobuf_arguments", generated_plugin_file_contents)
            self.assertIn("import plugin_name, gen_protobuf", generated_plugin_file_contents)
            self.assertIn("architecture_file", generated_plugin_file_contents)
            self.assertIn("output_directory", generated_plugin_file_contents)

            generated_plugin_impl_file_contents = generated_templates.get(PLUGIN_IMPL_TEMPLATE_NAME).content
            self.assertIn("def gen_protobuf", generated_plugin_impl_file_contents)
            self.assertIn("architecture_file (str)", generated_plugin_impl_file_contents)
            self.assertIn("output_directory (string)", generated_plugin_impl_file_contents)
            self.assertIn("with plugin_result", generated_plugin_impl_file_contents)
            self.assertIn("return result", generated_plugin_impl_file_contents)

            generated_plugin_impl_test_file_contents = generated_templates.get(PLUGIN_IMPL_TEST_TEMPLATE_NAME).content
            self.assertIn("TestAacGenProtobuf(TestCase)", generated_plugin_impl_test_file_contents)

            generated_readme_file_contents = generated_templates.get(README_TEMPLATE_NAME).content
            self.assertIn("# aac-gen-protobuf", generated_readme_file_contents)
            self.assertIn("## Command:", generated_readme_file_contents)
            self.assertIn("## Plugin Extensions and Definitions", generated_readme_file_contents)
            self.assertIn("$ aac gen-protobuf", generated_readme_file_contents)
            self.assertIn("### Ext", generated_readme_file_contents)
            self.assertIn("### Enum", generated_readme_file_contents)

            generated_tox_config_file_contents = generated_templates.get(TOX_CONFIG_TEMPLATE_NAME).content
            self.assertIn("[testenv]", generated_tox_config_file_contents)
            self.assertIn("[flake8]", generated_tox_config_file_contents)
            self.assertIn("[unittest]", generated_tox_config_file_contents)
            self.assertIn("[run]", generated_tox_config_file_contents)
            self.assertIn("[report]", generated_tox_config_file_contents)
            self.assertIn("code-directories = aac_gen_protobuf", generated_tox_config_file_contents)
            self.assertIn("coverage = aac_gen_protobuf", generated_tox_config_file_contents)
            self.assertIn("fail_under = 80.00", generated_tox_config_file_contents)

    def test__prepare_and_generate_plugin_files_errors_on_multiple_models(self):
        with validated_source(f"{TEST_PLUGIN_YAML_STRING}\n---\n{SECONDARY_MODEL_YAML_DEFINITION}") as result:
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


TEST_PLUGIN_NAME = "aac_gen_protobuf"

TEST_PLUGIN_YAML_STRING = """
model:
  name: aac-gen-protobuf
  description: aac-gen-protobuf is an Architecture-as-Code plugin that generates protobuf message definitions from Architecture-as-Code models.
  behavior:
    - name: gen-protobuf
      type: command
      description: Generate protobuf messages from Arch-as-Code models
      input:
        - name: architecture_file
          type: string
          python_type: str
          description: The yaml file containing the data models to generate as Protobuf messages.
        - name: output_directory
          type: string
          description: The directory to write the generated Protobuf messages to.
      acceptance:
        - scenario: Output protobuf messages for behavior input/output entries in an Architecture model.
          given:
            - The {{gen-protobuf.input.architecture_file}} contains a valid architecture.
          when:
            - The aac app is run with the gen-protobuf command and a valid architecture file.
          then:
            - Protobuf messages are written to {{gen-protobuf.input.output_directory}}.
---
enum:
  name: ProtobufDataType
  values:
    - double
    - float
    - int32
    - int64
    - uint32
    - uint64
    - sint32
    - sint64
    - fixed32
    - fixed64
    - bool
    - string
    - bytes
---
ext:
   name: ProtobufTypeField
   type: Field
   schemaExt:
      add:
        - name: protobuf_type
          type: ProtobufDataType
"""

SECONDARY_MODEL_YAML_DEFINITION = """
model:
  name: aac-spec-secondary
  description: aac-spec-secondary is a Architecture-as-Code plugin that enables requirement definition and trace in Arch-as-Code models.
  behavior:
    - name: spec-validate-2
      type: command
      description: 'Validates spec traces within the AaC model'
      input:
        - name: archFile
          type: file
        - name: parsed_model
          type: Map
      acceptance:
        - scenario: Valid spec traces are modeled.
          given:
            - The {{spec-validate.input.archFile}} contains a valid architecture specification.
            - The {{spec-validate.input.parsed_model}} contains the parsed content from archFile.
          when:
            - The aac app is run with the spec-validate command.
          then:
            - A message saying spec validation was successful is printed to the console.
    - name: non-cmd-behavior-2
      type: startup
      description: You shouldn't see me
      acceptance:
        - scenario: Pretend to do something on startup.
          when:
          - when
          then:
          - then
"""

MODEL_YAML_DEFINITION_SANS_PACKAGE_PREFIX = """
model:
  name: spec
  description: An Architecture-as-Code plugin that enables requirement definition and trace in Arch-as-Code models.
  behavior:
    - name: spec-validate
      type: command
      description: 'Validates spec traces within the AaC model'
      input:
        - name: archFile
          type: file
        - name: parsed_model
          type: Map
      acceptance:
        - scenario: Valid spec traces are modeled.
          given:
            - The {{spec-validate.input.archFile}} contains a valid architecture specification.
            - The {{spec-validate.input.parsed_model}} contains the parsed content from archFile.
          when:
            - The aac app is run with the spec-validate command.
          then:
            - A message saying spec validation was successful is printed to the console.
    - name: non-cmd-behavior-2
      type: startup
      description: You shouldn't see me
      acceptance:
        - scenario: Pretend to do something on startup.
          when:
          - when
          then:
          - then
"""
