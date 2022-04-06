from unittest import TestCase

from aac.plugins.help_dump.help_dump_impl import help_dump, _format_command, _get_all_commands
from aac.cli.aac_command import AacCommand, AacCommandArgument

from tests.helpers.assertion import assert_plugin_success


class TestHelpDump(TestCase):
    def test_format_command_line(self):
        command_name = "command-name"
        command_description = "A command description."
        command_arguments = [self.create_test_command_argument(f"arg{i}", f"The arg{i} description.") for i in range(3)]

        for i in range(3):
            expected = self.expected_formatted_command_string(
                command_name,
                command_description,
                i,
                [self.expected_formatted_command_argument_string(arg.name, arg.description) for arg in command_arguments[:i]]
            )
            actual = _format_command(self.create_test_command(command_name, command_description, command_arguments[:i]))

            self.assertEqual(expected, actual)

    def test_help_dump_prints_first_party_commands(self):
        result = help_dump()
        assert_plugin_success(result)

        for command_name in [cmd.name for cmd in _get_all_commands()]:
            self.assertIn(command_name, result.get_messages_as_string())

        for command_description in [cmd.description for cmd in _get_all_commands()]:
            self.assertIn(command_description, result.get_messages_as_string())

    def create_test_command(self, name, description, command_args):
        return AacCommand(name, description, lambda: f"Test Command: {name}\n{description}", command_args)

    def create_test_command_argument(self, name, description, number_of_arguments=None):
        return AacCommandArgument(name, description, number_of_arguments)

    def expected_formatted_command_string(self, command_name, command_description, num_args, command_arguments_strings):
        command_arguments_string = ("\n" if num_args > 0 else "") + "\n".join(command_arguments_strings)
        return f"{command_name}::{command_description}::{num_args}{command_arguments_string}"

    def expected_formatted_command_argument_string(self, argument_name, argument_description):
        return f"{argument_name}::{argument_description}"
