from unittest import TestCase
from tempfile import TemporaryDirectory, NamedTemporaryFile

from aac.plugins.gen_json.gen_json_impl import print_json
from aac.plugins.plugin_execution import PluginExecutionStatusCode, plugin_result


class Testgen_json(TestCase):

    def test_print_json_with_output_directory(self):

        with TemporaryDirectory() as temp_dir, NamedTemporaryFile("w") as temp_arch_file:
            temp_arch_file.write(TEST_ARCH_YAML_STRING)
            temp_arch_file.seek(0)

            with plugin_result("", print_json, [temp_arch_file.name], temp_dir) as result:
                self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_gen_json_output_to_cli(self):

        with TemporaryDirectory(), NamedTemporaryFile("w") as temp_arch_file:
            temp_arch_file.write(TEST_ARCH_YAML_STRING)
            temp_arch_file.seek(0)

            with plugin_result("", print_json, [temp_arch_file.name]) as result:
                self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_gen_json_with_invalid_arch_file(self):
        pass


TEST_ARCH_YAML_STRING = """
model:
  name: System
  description: A simple distributed system model
  components:
    - name: svc1
      type: ServiceOne
    - name: svc2
      type: ServiceTwo
  behavior:
    - name: doFlow
      type: request-response
      description:  process DataA and respond with DataD
      input:
        - name: in
          type: DataA
      output:
        - name: out
          type: DataC
      acceptance:
        - scenario: go
          given:
            - The System is running.
          when:
            - The System receives input.in
          then:
            - The System responds with output.out
---
data:
  name: DataA
  fields:
  - name: metadata
    type: MessageMetadataData
  - name: msg
    type: string
    protobuf_type: string
  - name: message_type
    type: MessageType
  required:
  - metadata
---
data:
  name: DataC
  fields:
  - name: metadata
    type: MessageMetadataData
  - name: code
    type: number[]
    protobuf_type: fixed64
  required:
  - metadata
---
data:
  name: MessageMetadataData
  fields:
  - name: message_id
    type: number
    protobuf_type: int64
  required:
  - message_id
"""
