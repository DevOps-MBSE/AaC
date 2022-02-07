from unittest import TestCase
from tempfile import TemporaryDirectory, NamedTemporaryFile

from aac.plugins.gen_json.gen_json_impl import print_json
from aac.plugins.plugin_execution import PluginExecutionStatusCode


class Testgen_json(TestCase):

    def test_print_json_with_output_directory(self):

        with TemporaryDirectory() as temp_dir, NamedTemporaryFile("w") as temp_arch_file:
            temp_arch_file.write(TEST_ARCH_YAML_STRING)
            temp_arch_file.seek(0)

            result = print_json([temp_arch_file.name], temp_dir):
            # TODO: Delete these once testing is complete
            print(result.messages)
            print(result.status_code)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self.assertIn("Wrote JSON to", "\n".join(result.messages))

    def test_gen_json_output_to_cli(self):

        with TemporaryDirectory(), NamedTemporaryFile("w") as temp_arch_file:
            temp_arch_file.write(TEST_ARCH_YAML_STRING)
            temp_arch_file.seek(0)

            result = print_json([temp_arch_file.name])
            # TODO: Delete these once testing is complete
            print(result.messages)
            print(result.status_code)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self.assertIn('"name": "Test_model"', "\n".join(result.messages))

    def test_gen_json_with_invalid_arch_file(self):
        pass


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
