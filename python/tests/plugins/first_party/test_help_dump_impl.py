import json

from unittest import TestCase
from collections import OrderedDict
from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins.first_party.help_dump.help_dump_impl import help_dump
from aac.plugins.plugin_manager import get_plugin_commands
from aac.serialization import AacCommandEncoder, AacCommandArgumentEncoder

from tests.helpers.assertion import assert_plugin_success


default_num_args = 5


class TestHelpDump(TestCase):
    def test_format_command_line(self):
        command_name = "command-name"
        command_description = "A command description."
        command_arguments = [
            AacCommandArgument(f"arg{i}", f"The arg{i} description.", data_type="str") for i in range(default_num_args)
        ]

        for i in range(3):
            expected = self.expected_formatted_output(command_name, command_description, command_arguments[:i])
            actual = AacCommandEncoder().default(AacCommand(command_name, command_description, lambda: None, command_arguments[:i]))

            self.assertDictEqual(expected, actual)

    def test_help_dump_prints_first_party_commands(self):
        result = help_dump()
        assert_plugin_success(result)

        for command in get_plugin_commands():
            self.assertIn(
                json.dumps(self.expected_formatted_output(command.name, command.description, command.arguments)),
                result.get_messages_as_string(),
            )

    def test_help_dump_json_dump_sort(self):
        expected_commands = sorted(get_plugin_commands(), key=lambda command: command.name)
        expected_result = [command.name for command in expected_commands]

        help_dump_output = json.loads(help_dump().get_messages_as_string(), object_pairs_hook=OrderedDict)
        actual_result = [command.get("name") for command in help_dump_output]

        self.assertListEqual(expected_result, actual_result)

    def expected_formatted_output(self, name, description, arguments):
        return {
            "name": name,
            "description": description,
            "arguments": [AacCommandArgumentEncoder().default(arg) for arg in arguments],
        }
