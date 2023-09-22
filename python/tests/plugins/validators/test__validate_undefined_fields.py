from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    DEFINITION_NAME_SCHEMA,
    PRIMITIVE_TYPE_STRING,
    ROOT_KEY_SCHEMA,
)
from aac.plugins.validators.undefined_fields._validate_undefined_fields import validate_undefined_fields, VALIDATION_NAME
from aac.validate import validated_definition, ValidationError

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_field_entry,
    create_schema_definition,
)


class TestUndefinedFieldsPlugin(ActiveContextTestCase):

    def test_validate_undefined_fields_invalid(self):

        # Create a test schema with a field `notADefinedFieldName` that is not defined in the `Schema` definition's fields.
        undefined_schema_field_name = "notADefinedFieldName"
        undefined_schema_field_value = "testString"
        test_schema_definition = create_schema_definition("TestSchema")

        # Manually insert the undefined field into the test definition's structure
        test_schema_definition.structure[ROOT_KEY_SCHEMA][undefined_schema_field_name] = undefined_schema_field_value

        # Re-parsing the test definition since the undefined field wasn't present when lexemes were calculated.
        test_schema_definition, *_ = parse(test_schema_definition.to_yaml())
        test_context = get_active_context()

        # Get the `Schema` definition since that defines the structure for all `schema` definitions.
        schema_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCHEMA)

        result = validate_undefined_fields(test_schema_definition, schema_definition, test_context)
        self.assertFalse(result.is_valid())

    def test_validate_undefined_fields_valid(self):

        # Create a valid instance of a schema definition.
        valid_schema_field = create_field_entry("someValidFieldEntry", PRIMITIVE_TYPE_STRING)
        test_schema_definition = create_schema_definition("TestSchema", fields=[valid_schema_field])

        test_context = get_active_context()

        # Get the `Schema` definition since that defines the structure for all `schema` definitions.
        schema_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCHEMA)

        result = validate_undefined_fields(test_schema_definition, schema_definition, test_context)
        self.assertTrue(result.is_valid())

    def test_validate_invalid_with_undefined_field_present(self):

        # Create a test schema with a field `notADefinedFieldName` that is not defined in the `Schema` definition's fields.
        undefined_schema_field_name = "notADefinedFieldName"
        undefined_schema_field_value = "testString"

        test_field = create_field_entry("testField", PRIMITIVE_TYPE_STRING)
        test_schema_definition = create_schema_definition("TestSchema", fields=[test_field])

        # Manually insert the undefined field into the test definition's structure
        test_schema_definition.structure[ROOT_KEY_SCHEMA][undefined_schema_field_name] = undefined_schema_field_value

        # Re-parsing the test definition since the undefined field wasn't present when lexemes were calculated.
        test_schema_definition, *_ = parse(test_schema_definition.to_yaml())

        validation_error = None
        try:
            with validated_definition(test_schema_definition):
                pass
        except Exception as error:
            validation_error = error
        finally:
            self.assertIsInstance(validation_error, ValidationError)
            self.assertIn(undefined_schema_field_name, str(validation_error))
            self.assertIn(VALIDATION_NAME, str(validation_error))

