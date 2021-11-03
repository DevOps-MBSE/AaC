from unittest import TestCase
from nose2.tools import params

from aac_gen_protobuf.aac_gen_protobuf_impl import _convert_camel_case_to_snake_case, _generate_protobuf_template_details_from_data_and_enum_models


class TestGenerateProtobufPlugin(TestCase):

    @params(("DataA", "data_a"), ("somethingSimple", "something_simple"), ("SomethingComplex!To.Test", "something_complex!_to._test"), ("whataboutnocamelcases?", "whataboutnocamelcases?"))
    def test__convert_camel_case_to_snake_case(self, test_string, expected_string):
        self.assertEqual(expected_string, _convert_camel_case_to_snake_case(test_string))

    def test__generate_protobuf_details_from_data_message_model(self):
        expected_result = {"name": "DataA", "file_type": "data", "fields": [{"name": "msg", "type": "int64", "optional": True, "repeat": False}]}
        test_model = {"DataA": {"data": {"name": "DataA", "fields": [{"name": "msg", "type": "number", "protobuf_type": "int64"}]}}}

        actual_result = _generate_protobuf_template_details_from_data_and_enum_models(test_model)
        self.assertDictEqual(expected_result, actual_result[0])

    def test__generate_protobuf_details_from_data_message_model_wth_repeated_fields(self):
        expected_result = {"name": "DataA", "file_type": "data", "fields": [{"name": "msg", "type": "int64", "optional": True, "repeat": True}]}
        test_model = {"DataA": {"data": {"name": "DataA", "fields": [{"name": "msg", "type": "number[]", "protobuf_type": "int64"}]}}}

        actual_result = _generate_protobuf_template_details_from_data_and_enum_models(test_model)
        self.assertDictEqual(expected_result, actual_result[0])

    def test__generate_protobuf_details_from_data_message_model_with_required_fields(self):
        expected_result = {"name": "DataA", "file_type": "data", "fields": [{"name": "id", "type": "int64", "optional": True, "repeat": False}, {"name": "msg", "type": "string", "optional": False, "repeat": False}]}
        test_model = {"DataA": {"data": {"name": "DataA", "fields": [{"name": "id", "type": "number", "protobuf_type": "int64"}, {"name": "msg", "type": "string", "protobuf_type": "string"}], "required": ["msg"]}}}

        actual_result = _generate_protobuf_template_details_from_data_and_enum_models(test_model)
        self.assertDictEqual(expected_result, actual_result[0])

    def test__generate_protobuf_details_from_data_message_model_with_nested_types_and_imports(self):
        expected_result = [
            {"name": "DataA", "file_type": "data", "fields": [{"name": "metadata", "type": "DataB", "optional": True, 'repeat': False}, {"name": "msg", "type": "string", "optional": True, "repeat": False}], "imports": ["data_b.proto"]},
            {"name": "DataB", "file_type": "data", "fields": [{"name": "id", "type": "int64", "optional": True, "repeat": False}]},
        ]

        test_model = {
            "DataA": {"data": {"name": "DataA", "fields": [{"name": "metadata", "type": "DataB"}, {"name": "msg", "type": "string", "protobuf_type": "string"}]}},
            "DataB": {"data": {"name": "DataB", "fields": [{"name": "id", "type": "number", "protobuf_type": "int64"}]}}
        }

        actual_result = _generate_protobuf_template_details_from_data_and_enum_models(test_model)
        for i in range(len(actual_result)):
            self.assertDictEqual(expected_result[i], actual_result[i])

    def test__generate_protobuf_details_from_data_message_model_with_enums(self):
        expected_result = [
            {"name": "DataA", "file_type": "data", "fields": [{"name": "message_type", "type": "Enum", "optional": True, "repeat": False}, {"name": "msg", "type": "string", "optional": True, "repeat": False}], "imports": ["enum.proto"]},
            {"name": "Enum", "file_type": "enum", "enums": ["VAL_1", "VAL_2"]},
        ]

        test_model = {
            "DataA": {"data": {"name": "DataA", "fields": [{"name": "message_type", "type": "Enum"}, {"name": "msg", "type": "string", "protobuf_type": "string"}]}},
            "Enum": {"enum": {"name": "Enum", "values": ["val_1", "val_2"]}}
        }

        actual_result = _generate_protobuf_template_details_from_data_and_enum_models(test_model)
        for i in range(len(actual_result)):
            print(actual_result[i])
            self.assertDictEqual(expected_result[i], actual_result[i])
