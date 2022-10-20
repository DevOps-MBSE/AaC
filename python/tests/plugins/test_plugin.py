from unittest.case import TestCase
from aac.plugins.plugin import Plugin

from tests.helpers.contribution_points import assert_items_are_registered, create_command, create_validation
from tests.helpers.parsed_definitions import create_schema_definition, create_validation_definition


class TestPlugin(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plugin = Plugin("test")

    def test_register_items(self):
        commands = {create_command("Test")}
        assert_items_are_registered(self, commands, self.plugin.register_commands, self.plugin.get_commands)

        validations = {create_validation("Test", create_validation_definition("validation"))}
        assert_items_are_registered(self, validations, self.plugin.register_definition_validations, self.plugin.get_definition_validations)

        definitions = {create_schema_definition("Test")}
        assert_items_are_registered(self, definitions, self.plugin.register_definitions, self.plugin.get_definitions)
