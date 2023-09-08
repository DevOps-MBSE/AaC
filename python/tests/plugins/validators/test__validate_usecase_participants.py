from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_NAME, DEFINITION_FIELD_SOURCE, DEFINITION_FIELD_TARGET, DEFINITION_NAME_USECASE
from aac.lang.definitions.collections import get_definition_by_name
from aac.plugins.validators.usecase_participants._validate_usecase_participants import validate_usecase_participants

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_field_entry,
    create_step_entry,
    create_usecase_definition,
)


class TestUsecaseParticipants(ActiveContextTestCase):
    def test_validate_usecase_with_referenced_participants(self):
        test_participant_1 = create_field_entry("user1", "SomeModel")
        test_participant_2 = create_field_entry("user2", "SomeOtherModel")
        test_step = create_step_entry(
            "step1", test_participant_1.get(DEFINITION_FIELD_NAME), test_participant_2.get(DEFINITION_FIELD_NAME), "action"
        )
        test_usecase = create_usecase_definition("TestUsecase", "", [test_participant_1, test_participant_2], [test_step])

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_usecase)
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_participants(test_usecase, target_schema_definition, test_active_context)

        self.assertTrue(result.is_valid())

    def test_usecase_with_step_endpoint_does_not_reference_participant_fails(self):
        test_participant = create_field_entry("user1", "SomeModel")
        test_step = create_step_entry("step1", "notUser1", "alsoNotUser1", "action")
        test_usecase = create_usecase_definition("TestUsecase", "", [test_participant], [test_step])

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_usecase)
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_participants(test_usecase, target_schema_definition, test_active_context)

        self.assertFalse(result.is_valid())

        source = test_step.get(DEFINITION_FIELD_SOURCE)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{source}.*not.*participant.*")

        target = test_step.get(DEFINITION_FIELD_TARGET)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{target}.*not.*participant.*")

    def test_validate_usecase_with_valid_source_invalid_target(self):
        test_participant = create_field_entry("user1", "SomeModel")
        test_step_valid_source = create_step_entry("step1", "user1", "notUser1", "action")
        test_usecase = create_usecase_definition("TestUsecase", "", [test_participant], [test_step_valid_source])

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_usecase)
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_participants(test_usecase, target_schema_definition, test_active_context)

        self.assertFalse(result.is_valid())

        source = test_step_valid_source.get(DEFINITION_FIELD_SOURCE)
        self.assertNotRegexpMatches(result.get_messages_as_string(), f".*{source}.*not.*participant.*")

        target = test_step_valid_source.get(DEFINITION_FIELD_TARGET)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{target}.*not.*participant.*")

    def test_validate_usecase_with_invalid_source_valid_target(self):
        test_participant = create_field_entry("user1", "SomeModel")
        test_step_valid_target = create_step_entry("step1", "notUser1", "user1", "action")
        test_usecase = create_usecase_definition("TestUsecase", "", [test_participant], [test_step_valid_target])

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_usecase)
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_participants(test_usecase, target_schema_definition, test_active_context)

        self.assertFalse(result.is_valid())

        source = test_step_valid_target.get(DEFINITION_FIELD_SOURCE)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{source}.*not.*participant.*")

        target = test_step_valid_target.get(DEFINITION_FIELD_TARGET)
        self.assertNotRegexpMatches(result.get_messages_as_string(), f".*{target}.*not.*participant.*")
