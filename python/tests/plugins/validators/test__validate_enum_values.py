from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import BEHAVIOR_TYPE_REQUEST_RESPONSE, DEFINITION_NAME_MODEL
from aac.plugins.validators import ValidatorResult
from aac.plugins.validators.enum_values._validate_enums import validate_enums
from aac.validate import validated_definition, ValidationError

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import create_behavior_entry, create_model_definition


class TestEnumValuesPlugin(ActiveContextTestCase):
    def test_validate_enum_values_valid(self):
        # Create a model with a behavior to test that the validation is valid when a valid BehaviorType enum value is used.
        test_behavior = create_behavior_entry("TestBehavior", BEHAVIOR_TYPE_REQUEST_RESPONSE)
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        expected_result = ValidatorResult()

        test_active_context = get_active_context(reload_context=True)
        model_schema_definition = test_active_context.get_definition_by_name(DEFINITION_NAME_MODEL)

        actual_result = validate_enums(test_model, model_schema_definition, test_active_context)

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())

    def test_validate_enum_values_invalid(self):
        # Create a model with a behavior to test that the validation is valid when a valid BehaviorType enum value is used.
        test_behavior = create_behavior_entry("TestBehavior", "NOT_A_VALID_BEHAVIOR_TYPE")
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        test_active_context = get_active_context(reload_context=True)
        model_schema_definition = test_active_context.get_definition_by_name(DEFINITION_NAME_MODEL)

        actual_result = validate_enums(test_model, model_schema_definition, test_active_context)

        self.assertFalse(actual_result.is_valid())

    def test_validated_definition_catches_invalid(self):
        # Create a model with a behavior to test that the validation is valid when a valid BehaviorType enum value is used.
        bad_enum_value = "NOT_A_VALID_BEHAVIOR_TYPE"
        test_behavior = create_behavior_entry("TestBehavior", bad_enum_value)
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        validation_message = ""
        try:
            with validated_definition(test_model):
                pass
        except Exception as validation_result:
            self.assertIsNotNone(validation_result)
            self.assertIsInstance(validation_result, ValidationError)
            validation_message = str(validation_result)

        # Setting up an assert outside the exception catch to demonstrate successful exception catching because assertRaise is inadequate.
        self.assertIn(test_model.name, validation_message)
        self.assertIn(bad_enum_value, validation_message)
