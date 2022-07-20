from typing import Callable
from unittest.case import TestCase

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.definitions.definition import Definition
from aac.plugins.contribution_points import ContributionPoints, InvalidContributionPointError
from aac.plugins.validators._validator_plugin import ValidatorPlugin

from tests.helpers.parsed_definitions import create_schema_definition, create_validation_definition


class TestContributionPoints(TestCase):
    plugin_name = "test"
    num_items_to_create = 2

    def setUp(self) -> None:
        super().setUp()
        self.contributions = ContributionPoints()

    def test_register_contributions(self):
        self._assert_items_are_registered(
            self.plugin_name,
            [create_command(f"Test{i}") for i in range(self.num_items_to_create)],
            self.contributions.register_commands,
            self.contributions.get_commands,
        )
        self._assert_items_are_registered(
            self.plugin_name,
            [
                create_validation(f"Test{i}", create_validation_definition(f"Validation{i}"))
                for i in range(self.num_items_to_create)
            ],
            self.contributions.register_validations,
            self.contributions.get_validations,
        )
        self._assert_items_are_registered(
            self.plugin_name,
            [create_schema_definition(f"Test{i}") for i in range(self.num_items_to_create)],
            self.contributions.register_definitions,
            self.contributions.get_definitions,
        )

    def test_get_contributions_by_name(self):
        command = create_command("Test")
        self.contributions.register_command(self.plugin_name, command)
        self.assertEqual(command, self.contributions.get_command_by_name(command.name))

        validation = create_validation("Test", create_validation_definition("Validation"))
        self.contributions.register_validation(self.plugin_name, validation)
        self.assertEqual(validation, self.contributions.get_validation_by_name(validation.name))

        definition = create_schema_definition("Test")
        self.contributions.register_definition(self.plugin_name, definition)
        self.assertEqual(definition, self.contributions.get_definition_by_name(definition.name))

    def test_register_validtaion_only_accepts_validations(self):
        make_regex = lambda item: f".*(error|add|validation|{item.name}).*".lower()

        definition = create_schema_definition("TestDefinition")
        self._assert_invalid_contribution_point(self.plugin_name, definition, make_regex(definition))

        command = create_command("TestCommand")
        self._assert_invalid_contribution_point(self.plugin_name, command, make_regex(command))

    def _assert_items_are_registered(self, name, items, register_fn, get_registered_items_fn):
        register_fn(name, items)

        registered_items = get_registered_items_fn(name)
        self.assertEqual(len(items), len(registered_items))
        [self.assertIn(item, registered_items) for item in items]

    def _assert_invalid_contribution_point(self, name, item, exception_regex):
        with self.assertRaises(InvalidContributionPointError) as cm:
            self.contributions.register_validation(name, item)

        self.assertRegex(cm.exception.message.lower(), exception_regex)


def identity(value: object) -> object:
    """Return the object that was passed in."""
    return value


def create_command(
        name: str, description: str = "", callback: Callable = identity, args: list[AacCommandArgument] = []
) -> AacCommand:
    """Create a new AacCommand for testing."""
    return AacCommand(name, description, callback, args)


def create_validation(name: str, definition: Definition, callback: Callable = identity) -> ValidatorPlugin:
    """Create a new ValidatorPlugin for testing."""
    return ValidatorPlugin(name, definition, callback)
