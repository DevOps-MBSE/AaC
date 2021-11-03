from unittest import TestCase
from nose2.tools import params

from aac_gen_protobuf.aac_gen_protobuf_impl import _convert_camel_case_to_snake_case, _generate_protobuf_template_details_from_data_message_models


class TestGenerateProtobufPlugin(TestCase):

    @params(("DataA", "data_a"), ("somethingSimple", "something_simple"), ("SomethingComplex!To.Test", "something_complex!_to._test"), ("whataboutnocamelcases?", "whataboutnocamelcases?"))
    def test__convert_camel_case_to_snake_case(self, test_string, expected_string):
        self.assertEqual(_convert_camel_case_to_snake_case(test_string), expected_string)

    def test__generate_protobuf_details_from_data_message_model(self):
        expected_result = {"name": "DataA", "fields": [{"name": "msg", "type": "int64", "optional": True}], "imports": []}
        test_model = {"DataA": {"data": {"name": "DataA", "fields": [{"name": "msg", "type": "number", "protobuf_type": "int64"}]}}}

        actual_result = _generate_protobuf_template_details_from_data_message_models(test_model)
        self.assertEqual(actual_result[0], expected_result)

    def test__generate_protobuf_details_from_data_message_model_with_required_fields(self):
        expected_result = {"name": "DataA", "fields": [{"name": "id", "type": "int64", "optional": True}, {"name": "msg", "type": "string", "optional": False}], "imports": []}
        test_model = {"DataA": {"data": {"name": "DataA", "fields": [{"name": "id", "type": "number", "protobuf_type": "int64"}, {"name": "msg", "type": "string", "protobuf_type": "string"}], "required": ["msg"]}}}

        actual_result = _generate_protobuf_template_details_from_data_message_models(test_model)
        self.assertDictEqual(actual_result[0], expected_result)

    def test__generate_protobuf_details_from_data_message_model_with_nested_types_and_imports(self):
        expected_result = [
            {"name": "DataA", "fields": [{"name": "metadata", "type": "DataB", "optional": True}, {"name": "msg", "type": "string", "optional": True}], "imports": ["data_b.proto"]},
            {"name": "DataB", "fields": [{"name": "id", "type": "int64", "optional": True}], "imports": []},
        ]

        test_model = {
            "DataA": {"data": {"name": "DataA", "fields": [{"name": "metadata", "type": "DataB"}, {"name": "msg", "type": "string", "protobuf_type": "string"}]}},
            "DataB": {"data": {"name": "DataB", "fields": [{"name": "id", "type": "number", "protobuf_type": "int64"}]}}
        }

        actual_result = _generate_protobuf_template_details_from_data_message_models(test_model)
        for i in range(len(actual_result)):
            self.assertDictEqual(actual_result[i], expected_result[i])
