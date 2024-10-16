from os.path import join, dirname
from unittest import TestCase

from aac.context.definition import Definition
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import AacCommandArgument, AacCommand, PluginRunner

class TestAacCommandArgument(TestCase):
    def test_init(self):
        arg = AacCommandArgument(name="test", description="test description", data_type="str")
        self.assertEqual(arg.name, "test")
        self.assertEqual(arg.description, "test description")
        self.assertEqual(arg.data_type, "str")
        self.assertEqual(arg.default, None)

    def test_invalid_name(self):
        with self.assertRaises(TypeError):
            AacCommandArgument(name=123, description="test description", data_type="str")

    def test_invalid_description(self):
        with self.assertRaises(TypeError):
            AacCommandArgument(name="test", description=123, data_type="str")

    def test_invalid_data_type(self):
        with self.assertRaises(TypeError):
            AacCommandArgument(name="test", description="test description", data_type=123)

class TestAacCommand(TestCase):
    def test_init(self):
        arg = AacCommandArgument(name="test", description="test description", data_type="str")
        callback = lambda: "Hello, World!"
        command = AacCommand(name="test_command", description="test command description", callback=callback, arguments=[arg])

        self.assertEqual(command.name, "test_command")
        self.assertEqual(command.description, "test command description")
        self.assertEqual(command.callback(), "Hello, World!")
        self.assertEqual(len(command.arguments), 1)
        self.assertEqual(command.arguments[0].name, "test")

    def test_invalid_name(self):
        with self.assertRaises(TypeError):
            AacCommand(name=123, description="test description", callback=lambda: None, arguments=[])

    def test_invalid_description(self):
        with self.assertRaises(TypeError):
            AacCommand(name="test", description=123, callback=lambda: None, arguments=[])

    def test_invalid_callback(self):
        with self.assertRaises(TypeError):
            AacCommand(name="test", description="test description", callback="not a function", arguments=[])

    def test_invalid_arguments(self):
        with self.assertRaises(TypeError):
            AacCommand(name="test", description="test description", callback=lambda: None, arguments="not a list")

class TestPluginRunner(TestCase):

    def test_plugin_runner(self):
        aac_file_path = join(dirname(__file__), "my_plugin.aac")
        context = LanguageContext()
        definitions = context.parse_and_load(aac_file_path)

        plugin_runner = PluginRunner(definitions[0], {}, {})
        plugin_runner.add_command_callback("command", lambda: "Command Callback")
        plugin_runner.add_constraint_callback("constraint", lambda: "Constraint Callback")

        command = plugin_runner.get_command_callback("command")
        constraint = plugin_runner.get_constraint_callback("constraint")
        self.assertEqual("Command Callback", command())
        self.assertEqual("Constraint Callback", constraint())
        self.assertEqual("My plugin", plugin_runner.get_plugin_name())


if __name__ == "__main__":
    unittest.main()
