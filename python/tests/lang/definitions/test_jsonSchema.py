import json

from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.definitions.jsonSchema import get_definition_as_json_schema
from aac.plugins.validators.required_fields import REQUIRED_FIELDS_VALIDATION_STRING

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestJsonSchema(TestCase):

    def test_get_definition_as_json_schema(self):
        self.maxDiff = None
        test_context = get_initialized_language_context(core_spec_only=True)

        test_sub_schema_enum_field = create_enum_definition("EnumField", ["val1", "val2"])

        test_sub_schema_name = "enumSchema"
        test_sub_schema = create_schema_definition(test_sub_schema_name, fields=[test_sub_schema_enum_field])

        test_root_schema_sub_schema_field = create_field_entry("SubSchemaField", test_sub_schema_name)
        test_root_schema_primitive_field = create_field_entry("PrimitiveField", "string")
        test_root_schema_name = "myDef"
        test_root_schema = create_schema_definition(test_root_schema_name, fields=[test_root_schema_primitive_field, test_root_schema_sub_schema_field])

        test_context.add_definitions_to_context([test_sub_schema, test_root_schema])

        expected_result = json.loads(EXPECTED_JSON_SCHEMA)
        actual_result = json.loads(get_definition_as_json_schema(test_root_schema, test_context))
        self.assertDictEqual(actual_result, expected_result)


EXPECTED_JSON_SCHEMA = """
{
    "$schema": "http://json-schema.org/draft/2020-12/schema",
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
                },
                "required": [
                    "name",
                    "type",
                    "description"
                ]
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
                            "title": "argument",
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name"
                ]
            }
        }
    },
    "required": [
        "name",
        "fields"
    ]
}
"""
