from unittest.case import TestCase

from aac.plugins.contributions.contribution_points import ContributionPoints

from tests.helpers.contribution_points import (
    create_command,
    create_validation,
    assert_invalid_contribution_point,
    assert_items_are_registered,
)
from tests.helpers.parsed_definitions import create_schema_definition, create_validation_definition


class TestContributionPoints(TestCase):
    plugin_name = "test"
    num_items = 2

    def setUp(self) -> None:
        super().setUp()
        self.contributions = ContributionPoints()

    def test_register_contributions(self):
        assert_items_are_registered(
            self,
            [create_command(f"Test{i}") for i in range(self.num_items)],
            lambda items: self.contributions.register_commands(self.plugin_name, items),
            self.contributions.get_commands,
        )
        assert_items_are_registered(
            self,
            [create_schema_definition(f"Test{i}") for i in range(self.num_items)],
            lambda items: self.contributions.register_definitions(self.plugin_name, items),
            self.contributions.get_definitions,
        )
        assert_items_are_registered(
            self,
            [
                create_validation(f"Test{i}", create_validation_definition(f"Validation{i}"))
                for i in range(self.num_items)
            ],
            lambda items: self.contributions.register_validations(self.plugin_name, items),
            self.contributions.get_validations,
        )

    def test_get_contributions_by_name(self):
        command = create_command("Test")
        definition = create_schema_definition("Test")
        validation = create_validation("Test", create_validation_definition("Validation"))

        self.contributions.register_command(self.plugin_name, command)
        self.contributions.register_definition(self.plugin_name, definition)
        self.contributions.register_validation(self.plugin_name, validation)

        self.assertEqual(command, self.contributions.get_command_by_name(command.name))
        self.assertEqual(definition, self.contributions.get_definition_by_name(definition.name))
        self.assertEqual(validation, self.contributions.get_validation_by_name(validation.name))

    def test_get_contributions_by_plugin(self):
        commands = [create_command(f"Test{i}") for i in range(self.num_items)]
        definitions = [create_schema_definition(f"Test{i}") for i in range(self.num_items)]
        validations = [
            create_validation(f"Test{i}", create_validation_definition(f"Validation{i}")) for i in range(self.num_items)
        ]

        self.contributions.register_commands(self.plugin_name, commands)
        self.contributions.register_definitions(self.plugin_name, definitions)
        self.contributions.register_validations(self.plugin_name, validations)

        self.assertCountEqual(self.contributions.get_commands_by_plugin_name(self.plugin_name), commands)
        self.assertCountEqual(self.contributions.get_definitions_by_plugin_name(self.plugin_name), definitions)
        self.assertCountEqual(self.contributions.get_validations_by_plugin_name(self.plugin_name), validations)

    def test_register_items_only_accept_items_of_correct_contribution_type(self):
        make_regex = lambda expected, item: f".*(error|add|{expected}|{item.name}).*".lower()

        command = create_command("TestCommand")
        definition = create_schema_definition("TestDefinition")
        validation = create_validation("TestValidation", create_validation_definition("Validation"))

        def assertion(item, register_fn, regex):
            assert_invalid_contribution_point(self, self.plugin_name, item, register_fn, regex)

        assertion(definition, self.contributions.register_command, make_regex("command", definition))
        assertion(validation, self.contributions.register_command, make_regex("command", validation))

        assertion(command, self.contributions.register_definition, make_regex("definition", command))
        assertion(validation, self.contributions.register_definition, make_regex("definition", validation))

        assertion(definition, self.contributions.register_validation, make_regex("validation", definition))
        assertion(command, self.contributions.register_validation, make_regex("validation", command))
