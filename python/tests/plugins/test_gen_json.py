import os

from aac.plugins.gen_json.gen_json_impl import print_json
from aac.plugins.plugin_execution import PluginExecutionStatusCode

from tests.base_test_case import BaseTestCase
from tests.helpers.assertion import assert_plugin_success
from tests.helpers.io import temporary_test_file


class TestGenJson(BaseTestCase):
    def test_print_json_with_output_directory(self):
        with temporary_test_file(TEST_ARCH_YAML_STRING) as temp_arch_file:
            temp_dir = os.path.dirname(temp_arch_file.name)
            result = print_json([temp_arch_file.name], temp_dir)
            assert_plugin_success(result)
            self.assertIn("Wrote JSON to", "\n".join(result.messages))

    def test_gen_json_with_output_directory_that_does_not_exist(self):
        with temporary_test_file(TEST_ARCH_YAML_STRING) as temp_arch_file:
            temp_dir = os.path.join(os.path.dirname(temp_arch_file.name), "does", "not", "exist")
            self.assertFalse(os.path.exists(temp_dir))
            result = print_json([temp_arch_file.name], temp_dir)
            assert_plugin_success(result)
            self.assertTrue(os.path.exists(temp_dir))

    def test_gen_json_output_to_cli(self):
        with temporary_test_file(TEST_ARCH_YAML_STRING) as temp_arch_file:
            result = print_json([temp_arch_file.name])
            assert_plugin_success(result)
            self.assertIn('"name": "Test_model"', "\n".join(result.messages))

    def test_gen_json_with_invalid_arch_file(self):
        with temporary_test_file(BAD_YAML_STRING) as temp_arch_file:
            result = print_json([temp_arch_file.name])
            self.assertEqual(result.status_code, PluginExecutionStatusCode.VALIDATION_FAILURE)

    def test_gen_json_with_unparsable_file(self):
        with temporary_test_file("model: ][") as temp_arch_file:
            result = print_json([temp_arch_file.name])
            self.assertEqual(result.status_code, PluginExecutionStatusCode.PARSER_FAILURE)


TEST_ARCH_YAML_STRING = """
model:
  name: Test_model
  description: A Test Yaml file.
  behavior:
    - name: Test
      type: command
      description: Tests Yaml
      input:
        - name: architecture_file
          type: string
"""

BAD_YAML_STRING = """
model:
  name: Test_model
  description: A Test Yaml file.
  behavior:
    - Name: Test
      type: command
      description: Tests Yaml
      input:
        - name: architecture
          type: striiiiiiiiiiiiiiing
"""
