from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.validators.subcomponent_type._subcomponent_type import validate_subcomponent_types

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import create_schema_definition, create_field_entry, create_model_definition
from tests.helpers.assertion import assert_validator_result_failure, assert_validator_result_success


class TestValidationSubcomponentTypes(ActiveContextTestCase):
    def test_validation_of_model_definition_with_no_subcomponents(self):
        test_active_context = get_active_context()

        model_name = "A model"
        def_with_no_subcomponents = create_model_definition(model_name)

        test_active_context.add_definition_to_context(def_with_no_subcomponents)
        target_sub_definition = test_active_context.get_definition_by_name("model")

        actual_result = validate_subcomponent_types(def_with_no_subcomponents, target_sub_definition, test_active_context)
        assert_validator_result_success(actual_result)

    def test_validation_of_model_definition_with_model_subcomponents(self):
        test_active_context = get_active_context()

        model_name = "A model"
        valid_subcomponent = create_model_definition("subcomponent")
        def_with_subcomponents = create_model_definition(
            model_name,
            components=[create_field_entry("a", valid_subcomponent.name)],
        )

        test_active_context.add_definitions_to_context([def_with_subcomponents, valid_subcomponent])
        target_sub_definition = test_active_context.get_definition_by_name("model")

        actual_result = validate_subcomponent_types(def_with_subcomponents, target_sub_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validation_of_model_definition_with_non_model_subcomponents(self):
        test_active_context = get_active_context()

        model_name = "A model"
        invalid_subcomponent = create_schema_definition("invalid subcomponent")
        definition_with_invalid_subcomponents = create_model_definition(
            model_name,
            components=[create_field_entry("a", invalid_subcomponent.name)],
        )

        test_active_context.add_definitions_to_context([definition_with_invalid_subcomponents, invalid_subcomponent])
        target_sub_definition = test_active_context.get_definition_by_name("model")

        actual_result = validate_subcomponent_types(definition_with_invalid_subcomponents, target_sub_definition, test_active_context)

        assert_validator_result_failure(actual_result, "subcomponent type")

    def test_validation_of_model_definition_with_subcomponent_missing_type(self):
        test_active_context = get_active_context()

        model_name = "A model"
        invalid_subcomponent_name = "invalid subcomponent"
        definition_with_invalid_subcomponents = create_model_definition(
            model_name,
            components=[create_field_entry(invalid_subcomponent_name)],
        )

        test_active_context.add_definition_to_context(definition_with_invalid_subcomponents)
        target_sub_definition = test_active_context.get_definition_by_name("model")

        actual_result = validate_subcomponent_types(definition_with_invalid_subcomponents, target_sub_definition, test_active_context)
        assert_validator_result_failure(actual_result, "component", invalid_subcomponent_name, "not", "present")
