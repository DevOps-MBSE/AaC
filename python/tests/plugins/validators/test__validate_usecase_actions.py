from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    DEFINITION_FIELD_ACTION,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_SOURCE,
    DEFINITION_NAME_USECASE,
)
from aac.lang.definitions.collections import get_definition_by_name
from aac.plugins.validators.usecase_actions._validate_usecase_actions import validate_usecase_actions

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_field_entry,
    create_model_definition,
    create_step_entry,
    create_usecase_definition,
)


class TestValidateUsecaseActions(ActiveContextTestCase):
    def test_validate_usecase_with_referenced_behaviors(self):
        test_behavior_1 = create_behavior_entry("behavior1")
        test_behavior_2 = create_behavior_entry("behavior2")
        test_model_1 = create_model_definition("SomeModel", behavior=[test_behavior_1, test_behavior_2])
        test_model_2 = create_model_definition("SomeOtherModel")

        test_participants = [create_field_entry("user1", test_model_1.name), create_field_entry("user2", test_model_2.name)]
        test_participant_names = [participant.get(DEFINITION_FIELD_NAME) for participant in test_participants]

        test_step_1 = create_step_entry("step1", *test_participant_names, test_behavior_1.get(DEFINITION_FIELD_NAME))
        test_step_2 = create_step_entry("step2", *test_participant_names, test_behavior_2.get(DEFINITION_FIELD_NAME))

        test_usecase = create_usecase_definition(
            "TestUsecase", participants=test_participants, steps=[test_step_1, test_step_2]
        )

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definitions_to_context([test_usecase, test_model_1, test_model_2])
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_actions(test_usecase, target_schema_definition, test_active_context)

        self.assertTrue(result.is_valid())

    def test_usecase_with_action_does_not_reference_source_model_behavior_fails(self):
        test_behavior = create_behavior_entry("an action")
        test_model_1 = create_model_definition("SomeModel")
        test_model_2 = create_model_definition("SomeOtherModel", behavior=[test_behavior])
        test_participant_1 = create_field_entry("user1", test_model_1.name)
        test_participant_2 = create_field_entry("user2", test_model_2.name)
        test_step_1 = create_step_entry(
            "step1",
            test_participant_1.get(DEFINITION_FIELD_NAME),
            test_participant_2.get(DEFINITION_FIELD_NAME),
            test_behavior.get(DEFINITION_FIELD_NAME),
        )
        test_step_2 = create_step_entry(
            "step2",
            test_participant_2.get(DEFINITION_FIELD_NAME),
            test_participant_1.get(DEFINITION_FIELD_NAME),
            "another action",
        )
        test_usecase = create_usecase_definition(
            "TestUsecase", participants=[test_participant_1, test_participant_2], steps=[test_step_1, test_step_2]
        )

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definitions_to_context([test_usecase, test_model_1, test_model_2])
        target_schema_definition = get_definition_by_name(DEFINITION_NAME_USECASE, test_active_context.definitions)

        result = validate_usecase_actions(test_usecase, target_schema_definition, test_active_context)

        self.assertFalse(result.is_valid())

        action_name = test_step_1.get(DEFINITION_FIELD_ACTION)
        source_name = test_step_1.get(DEFINITION_FIELD_SOURCE)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{action_name}.*not.*behavior.*{source_name}.*")

        action_name = test_step_2.get(DEFINITION_FIELD_ACTION)
        source_name = test_step_2.get(DEFINITION_FIELD_SOURCE)
        self.assertRegexpMatches(result.get_messages_as_string(), f".*{action_name}.*not.*behavior.*{source_name}.*")
