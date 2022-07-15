from typing import Callable
from unittest.case import TestCase

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.definitions.definition import Definition
from aac.plugins.contribution_points import ContributionPointNames, ContributionPoints, InvalidContributionPointError
from aac.plugins.validators._validator_plugin import ValidatorPlugin

from tests.helpers.parsed_definitions import create_enum_definition, create_schema_definition, create_validation_definition


class TestContributionPoints(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.contributions = ContributionPoints()

    def test_register_contributions(self):
        self._assert_items_are_registered(
            ContributionPointNames.COMMANDS,
            [create_command("Test1"), create_command("Test2")],
            self.contributions.register_commands,
        )
        self._assert_items_are_registered(
            ContributionPointNames.VALIDATIONS,
            [
                create_validation("Test1", create_validation_definition("Validation1")),
                create_validation("Test2", create_validation_definition("Validation2"))
            ],
            self.contributions.register_validations,
        )
        self._assert_items_are_registered(
            ContributionPointNames.DEFINITIONS,
            [create_schema_definition("Test1"), create_enum_definition("Test2", ["one", "two"])],
            self.contributions.register_definitions,
        )

    def test_register_validtaion_only_accepts_validations(self):
        make_regex = lambda item: f".*(error|add|validation|{item.name}).*".lower()

        definition = create_schema_definition("TestDefinition")
        self._assert_invalid_contribution_point(definition, make_regex(definition))

        command = create_command("TestCommand")
        self._assert_invalid_contribution_point(command, make_regex(command))

    def _assert_items_are_registered(self, contribution_point_name, items, register_fn):
        register_fn(items)

        registered_items = self.contributions.contribution_points.get(contribution_point_name, [])
        self.assertEqual(len(items), len(registered_items))
        [self.assertIn(item, registered_items) for item in items]

    def _assert_invalid_contribution_point(self, item, exception_regex):
        with self.assertRaises(InvalidContributionPointError) as cm:
            self.contributions.register_validation(item)

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
