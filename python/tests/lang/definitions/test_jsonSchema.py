import json

from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.definitions.jsonSchema import get_definition_json_schema

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_enum_definition,
    create_field_entry,
)


class TestJsonSchema(TestCase):
    def test_get_definition_json_schema_with_schema_definition(self):
        self.maxDiff = None
        test_context = get_initialized_language_context(core_spec_only=True)

        test_sub_schema_enum_field = create_enum_definition("EnumField", ["val1", "val2"])

        test_sub_schema_name = "enumSchema"
        test_sub_schema = create_schema_definition(test_sub_schema_name, fields=[test_sub_schema_enum_field])

        test_root_schema_sub_schema_field = create_field_entry("SubSchemaField", test_sub_schema_name)
        test_root_schema_primitive_field = create_field_entry("PrimitiveField", "string")
        test_root_schema_name = "myDef"
        test_root_schema = create_schema_definition(
            test_root_schema_name, fields=[test_root_schema_primitive_field, test_root_schema_sub_schema_field]
        )

        test_context.add_definitions_to_context([test_sub_schema, test_root_schema])

        expected_result = json.loads(EXPECTED_JSON_SCHEMA)
        actual_result = json.loads(get_definition_json_schema(test_root_schema, test_context))
        self.assertDictEqual(actual_result, expected_result)

    def test_get_definition_json_schema_with_enum(self):
        self.maxDiff = None
        test_context = get_initialized_language_context(core_spec_only=True)

        test_sub_schema_enum_field = create_enum_definition("EnumField", ["val1", "val2"])

        test_sub_schema_name = "enumSchema"
        test_sub_schema = create_schema_definition(test_sub_schema_name, fields=[test_sub_schema_enum_field])

        test_root_schema_sub_schema_field = create_field_entry("SubSchemaField", test_sub_schema_name)
        test_root_schema_primitive_field = create_field_entry("PrimitiveField", "string")
        test_root_schema_name = "myDef"
        test_root_schema = create_schema_definition(
            test_root_schema_name, fields=[test_root_schema_primitive_field, test_root_schema_sub_schema_field]
        )

        test_context.add_definitions_to_context([test_sub_schema, test_root_schema])

        expected_result = json.loads(EXPECTED_JSON_SCHEMA)
        actual_result = json.loads(get_definition_json_schema(test_root_schema, test_context))
        self.assertDictEqual(actual_result, expected_result)


EXPECTED_JSON_SCHEMA = """
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "fields": {
            "type": "array",
            "items":
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        },
        "validation": {
            "type": "array",
            "items":
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "arguments": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
}
"""
