from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import BEHAVIOR_TYPE_REQUEST_RESPONSE, DEFINITION_NAME_MODEL
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution
from aac.plugins.validators import ValidatorFindings, ValidatorResult
from aac.plugins.validators.defined_references import _get_plugin_definitions, _get_plugin_validations, validate_references
from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_definitions_equal
from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import create_behavior_entry, create_field_entry, create_model_definition, create_schema_definition


class TestEnumValuesPlugin(ActiveContextTestCase):
    def test_validate_enum_values_valid(self):
        # Create a model with a behavior to test that the validation is valid when a valid BehaviorType enum value is used.
        test_behavior = create_behavior_entry("TestBehavior", BEHAVIOR_TYPE_REQUEST_RESPONSE)
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        expected_result = ValidatorResult()

        test_active_context = get_active_context(reload_context=True)
        model_schema_definition = test_active_context.get_definition_by_name(DEFINITION_NAME_MODEL)

        actual_result = validate_references(test_model, model_schema_definition, test_active_context)

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())

    def test_validate_enum_values_invalid(self):
        # Create a model with a behavior to test that the validation is valid when a valid BehaviorType enum value is used.
        test_behavior = create_behavior_entry("TestBehavior", "NOT_A_VALID_BEHAVIOR_TYPE")
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        test_active_context = get_active_context(reload_context=True)
        model_schema_definition = test_active_context.get_definition_by_name(DEFINITION_NAME_MODEL)

        actual_result = validate_references(test_model, model_schema_definition, test_active_context)

        self.assertFalse(actual_result.is_valid())

