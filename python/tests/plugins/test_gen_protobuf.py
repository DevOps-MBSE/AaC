from nose2.tools import params
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest.mock import patch
import logging
import os

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.plugin_execution import plugin_result
from aac.plugins.gen_protobuf.gen_protobuf_impl import (
    gen_protobuf,
    _convert_message_name_to_file_name,
    _convert_camel_case_to_snake_case,
    _get_message_template_properties,
    _convert_description_to_protobuf_comment
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_failure, assert_plugin_success
from tests.helpers.io import temporary_test_file
from tests.helpers.parsed_definitions import create_enum_definition, create_field_entry, create_schema_definition


TEST_MESSAGE_A_NAME = "MessageA"
TEST_MESSAGE_A_DESCRIPTION = "Some description for MessageA"
TEST_MESSAGE_B_NAME = "MessageB"
TEST_MESSAGE_B_FILE_NAME = "message_b.proto"
TEST_FIELD_A_NAME = "test_field_a"
TEST_FIELD_A_DESCRIPTION = "Some description for TestFieldA"
FIELD_METADATA_NAME = "metadata"
FIELD_MESSAGE_NAME = "message"
FIELD_ID_NAME = "id"
INT64_TYPE = "int64"
STRING_TYPE = "string"
SCHEMA_FILE_TYPE = "schema"
ENUM_FILE_TYPE = "enum"
ENUM_VALUE_1 = "VAL1"
ENUM_VALUE_2 = "VAL2"


class TestGenerateProtobufPlugin(ActiveContextTestCase):
    def setUp(self) -> None:
        super().setUp()
        logging.disable()  # Hide the error messages generated by these tests from the console.
        self.maxDiff = None

    def test_gen_protobuf(self):
        with TemporaryDirectory() as temp_dir, temporary_test_file(TEST_ARCH_YAML_STRING) as temp_arch_file:
            with plugin_result("", gen_protobuf, temp_arch_file.name, temp_dir) as result:
                pass

            # The assert needs to be outside of the plugin_result context manager or the assertion error is masked.
            assert_plugin_success(result)

            # Assert each data message has its own file.
            generated_file_names = os.listdir(temp_dir)
            self.assertEqual(5, len(generated_file_names))

            # Assert each expected file is present
            self.assertIn("data_a.proto", generated_file_names)
            self.assertIn("data_b.proto", generated_file_names)
            self.assertIn("data_c.proto", generated_file_names)
            self.assertIn("message_metadata_data.proto", generated_file_names)
            self.assertIn("message_type.proto", generated_file_names) 

            # Assert data_a.proto contents
            with open(os.path.join(temp_dir, "data_a.proto")) as data_a_proto_file:
                data_a_proto_file_contents = data_a_proto_file.read()
                # Assert imports for component classes
                self.assertIn('import "message_metadata_data.proto"', data_a_proto_file_contents)
                self.assertIn('import "message_type.proto"', data_a_proto_file_contents)

                # Assert Data A Message Descripton
                self.assertIn('Description for the DataA Message', data_a_proto_file_contents)
                self.assertIn('Description for the DataA MessageMetadataData', data_a_proto_file_contents)

                # Assert data_a structure
                self.assertIn("MessageMetadataData metadata", data_a_proto_file_contents)
                self.assertIn("string msg", data_a_proto_file_contents)
                self.assertIn("MessageType message_type", data_a_proto_file_contents)

            # Assert data_b.proto contents
            with open(os.path.join(temp_dir, "data_b.proto")) as data_b_proto_file:
                data_b_proto_file_contents = data_b_proto_file.read()
                # Assert imports for component classes
                self.assertIn('import "message_metadata_data.proto"', data_b_proto_file_contents)

                # Assert Options for the protobuf message
                self.assertIn('option java_package = "com.example.foo";', data_b_proto_file_contents)
                self.assertIn('option boolean_property = false;', data_b_proto_file_contents)

                # Assert data_b structure
                self.assertIn("MessageMetadataData metadata", data_b_proto_file_contents)
                self.assertIn("string transformed_msg", data_b_proto_file_contents)

            # Assert data_c.proto contents
            with open(os.path.join(temp_dir, "data_c.proto")) as data_c_proto_file:
                data_c_proto_file_contents = data_c_proto_file.read()
                # Assert imports for component classes
                self.assertIn('import "message_metadata_data.proto"', data_c_proto_file_contents)

                # Assert data_b structure
                self.assertIn("MessageMetadataData metadata", data_c_proto_file_contents)
                self.assertIn("repeated fixed64 code", data_c_proto_file_contents)

            # Assert message_metadata_data.proto contents
            with open(os.path.join(temp_dir, "message_metadata_data.proto")) as message_metadata_data_proto_file:
                message_metadata_data_proto_file_contents = message_metadata_data_proto_file.read()

                # Assert data_b structure
                self.assertIn("message MessageMetadataData", message_metadata_data_proto_file_contents)
                self.assertIn("int64 message_id", message_metadata_data_proto_file_contents)

            # Assert message_type.proto contents
            with open(os.path.join(temp_dir, "message_type.proto")) as message_type_proto_file:
                message_type_proto_file_contents = message_type_proto_file.read()

                # Assert message_type structure
                self.assertIn("enum MessageType", message_type_proto_file_contents)
                self.assertIn("TYPE_1", message_type_proto_file_contents)
                self.assertIn("TYPE_2", message_type_proto_file_contents)
                self.assertIn("TYPE_3", message_type_proto_file_contents)

    @patch("aac.plugins.gen_protobuf.gen_protobuf_impl.load_templates")
    def test_gen_protobuf_fails_with_multiple_message_templates(self, load_templates):
        with TemporaryDirectory() as temp_dir, NamedTemporaryFile("w") as arch_file:
            arch_file.write(TEST_ARCH_YAML_STRING)
            arch_file.seek(0)

            load_templates.return_value = ["a", "b"]
            result = gen_protobuf(arch_file.name, temp_dir)
            assert_plugin_failure(result)

    @params(
        ("DataA", "data_a"),
        ("somethingSimple", "something_simple"),
        ("SomethingComplex!To.Test", "something_complex!_to._test"),
        ("whataboutnocamelcases?", "whataboutnocamelcases?"),
    )
    def test__convert_camel_case_to_snake_case(self, test_string, expected_string):
        self.assertEqual(expected_string, _convert_camel_case_to_snake_case(test_string))

    @params(
        ("Data A", "data_a.proto"),
        ("Message with multiple spaces", "messagewithmultiplespaces.proto"),
        (" beginningSpace", "beginning_space.proto"),
        ("trailing ", "trailing.proto"),
    )
    def test__convert_message_name_to_file_name(self, test_string, expected_string):
        self.assertEqual(expected_string, _convert_message_name_to_file_name(test_string))

    def test__generate_protobuf_details_from_data_message_model(self):
        test_field = _to_message_template_field_properties(TEST_FIELD_A_NAME, INT64_TYPE, TEST_FIELD_A_DESCRIPTION)
        expected_result = _to_message_template_properties(TEST_MESSAGE_A_NAME, TEST_MESSAGE_A_DESCRIPTION, SCHEMA_FILE_TYPE, [test_field])

        test_message_field = create_field_entry(TEST_FIELD_A_NAME, INT64_TYPE, TEST_FIELD_A_DESCRIPTION)

        test_message_definition = create_schema_definition(TEST_MESSAGE_A_NAME, TEST_MESSAGE_A_DESCRIPTION, [test_message_field])

        actual_result = _get_message_template_properties({test_message_definition.name: test_message_definition})
        self.assertDictEqual(expected_result, actual_result[0])

    def test__generate_protobuf_details_from_data_message_model_wth_repeated_fields(self):
        test_field = _to_message_template_field_properties(TEST_FIELD_A_NAME, INT64_TYPE, repeat=True)
        expected_result = _to_message_template_properties(TEST_MESSAGE_A_NAME, TEST_MESSAGE_A_DESCRIPTION, SCHEMA_FILE_TYPE, [test_field])

        test_message_field = create_field_entry(TEST_FIELD_A_NAME, f"{INT64_TYPE}[]")
        test_message_definition = create_schema_definition(TEST_MESSAGE_A_NAME, TEST_MESSAGE_A_DESCRIPTION, [test_message_field])

        actual_result = _get_message_template_properties({test_message_definition.name: test_message_definition})
        self.assertDictEqual(expected_result, actual_result[0])

    def test__generate_protobuf_details_from_data_message_model_with_nested_types_and_imports(self):
        expected_field_metadata = _to_message_template_field_properties(FIELD_METADATA_NAME, TEST_MESSAGE_B_NAME)
        expected_field_msg = _to_message_template_field_properties(FIELD_MESSAGE_NAME, STRING_TYPE)
        expected_field_id = _to_message_template_field_properties(FIELD_ID_NAME, INT64_TYPE)

        expected_message_a = _to_message_template_properties(TEST_MESSAGE_A_NAME, "", SCHEMA_FILE_TYPE, [expected_field_metadata, expected_field_msg], imports=[TEST_MESSAGE_B_FILE_NAME])
        expected_message_b = _to_message_template_properties(TEST_MESSAGE_B_NAME, "", SCHEMA_FILE_TYPE, [expected_field_id])

        expected_result = [expected_message_a, expected_message_b]

        test_message_field = create_field_entry(FIELD_MESSAGE_NAME, STRING_TYPE)
        test_metadata_field = create_field_entry(FIELD_METADATA_NAME, TEST_MESSAGE_B_NAME)
        test_id_field = create_field_entry(FIELD_ID_NAME, INT64_TYPE)

        test_message_a_definition = create_schema_definition(TEST_MESSAGE_A_NAME, fields=[test_metadata_field, test_message_field])
        test_message_b_definition = create_schema_definition(TEST_MESSAGE_B_NAME, fields=[test_id_field])

        test_definitions_dict = {d.name: d for d in [test_message_a_definition, test_message_b_definition]}
        actual_result = _get_message_template_properties(test_definitions_dict)
        for i in range(len(actual_result)):
            self.assertDictEqual(expected_result[i], actual_result[i])

    def test__generate_protobuf_details_from_data_message_model_with_enums(self):
        expected_field_message_type = _to_message_template_field_properties(TEST_FIELD_A_NAME, TEST_MESSAGE_B_NAME)
        expected_field_msg = _to_message_template_field_properties(FIELD_MESSAGE_NAME, STRING_TYPE)

        expected_message_a = _to_message_template_properties(TEST_MESSAGE_A_NAME, "", SCHEMA_FILE_TYPE, [expected_field_message_type, expected_field_msg], imports=[TEST_MESSAGE_B_FILE_NAME])
        expected_message_b = _to_message_template_properties(TEST_MESSAGE_B_NAME, "", ENUM_FILE_TYPE, enums=[ENUM_VALUE_1, ENUM_VALUE_2])

        expected_result = [expected_message_a, expected_message_b]

        test_field_message_type = create_field_entry(TEST_FIELD_A_NAME, TEST_MESSAGE_B_NAME)
        test_field_message = create_field_entry(FIELD_MESSAGE_NAME, STRING_TYPE)

        test_message_a_definition = create_schema_definition(TEST_MESSAGE_A_NAME, fields=[test_field_message_type, test_field_message])
        test_enum_definition = create_enum_definition(TEST_MESSAGE_B_NAME, [ENUM_VALUE_1, ENUM_VALUE_2])

        test_definitions = test_message_a_definition, test_enum_definition
        get_active_context().add_definitions_to_context(test_definitions)

        test_definitions_dict = {d.name: d for d in test_definitions}
        actual_result = _get_message_template_properties(test_definitions_dict)
        for i in range(len(actual_result)):
            self.assertDictEqual(expected_result[i], actual_result[i])


def _to_message_template_properties(
    name: str,
    description: str = "",
    file_type: str = SCHEMA_FILE_TYPE,
    fields: list = [],
    enums: list = [],
    imports: list = [],
    options: list = [],
) -> dict:
    """Provides a simple interface for creating message template property dicts."""
    return {
        "message_name": name,
        "message_description": _convert_description_to_protobuf_comment(description),
        "file_type": file_type,
        "fields": fields,
        "enums": enums,
        "imports": imports,
        "options": options,
    }


def _to_message_template_field_properties(name: str, type: str, description: str = "", repeat: bool = False) -> dict:
    """Provides a simple interface for creating message template field property dicts, used to populate the `fields` value in the `_to_message_template_properties` function."""
    return {
        "name": name,
        "description": _convert_description_to_protobuf_comment(description),
        "type": type,
        "repeat": repeat
    }


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
          type: Data A
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
          type: Data A
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
---
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
schema:
  name: Data A
  description: Description for the DataA Message
  fields:
  - name: metadata
    type: MessageMetadataData
    description: Description for the DataA MessageMetadataData
  - name: msg
    type: string
  - name: message_type
    type: Message Type
  validation:
    - name: Required fields are present
      arguments:
        - metadata
---
schema:
  name: DataB
  protobuf_message_options:
    - key: java_package
      value: "com.example.foo"
    - key: boolean_property
      value: false
  fields:
  - name: metadata
    type: MessageMetadataData
  - name: transformed_msg
    type: string
  validation:
    - name: Required fields are present
      arguments:
        - metadata
        - transformed_msg
---
schema:
  name: DataC
  fields:
    - name: metadata
      type: MessageMetadataData
    - name: code
      type: fixed64[]
  validation:
    - name: Required fields are present
      arguments:
        - metadata
---
schema:
  name: MessageMetadataData
  fields:
    - name: message_id
      type: int64
  validation:
    - name: Required fields are present
      arguments:
        - message_id
---
enum:
  name: Message Type
  values:
    - type 1
    - type 2
    - type 3
"""
