
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
model:
  name: ServiceOne
  behavior:
    - name: ProcessDataA
      type: request-response
      input:
        - name: in
          type: DataA
      output:
        - name: out
          type: DataB
      acceptance:
        - scenario: go
          given:
            - ServiceOne is running.
          when:
            - The user sends a DataA request
          then:
            - The user receives a DataB response
model:
  name: ServiceTwo
  behavior:
    - name: Process DataB
      type: request-response
      input:
        - name: in
          type: DataB
      output:
        - name: out
          type: DataC
      acceptance:
        - scenario: go
          given:
            - The ServiceTwo is running
          when:
            - The user makes a request with DataB
          then:
            - The user receives a response with DataC
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
  name: DataB
  fields:
  - name: metadata
    type: MessageMetadataData
  - name: transformed_msg
    type: string
    protobuf_type: string
  required:
  - metadata
  - transformed_msg
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
---
enum:
  name: MessageType
  values:
  - type_1
  - type_2
  - type_3
"""
