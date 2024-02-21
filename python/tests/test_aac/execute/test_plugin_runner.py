import unittest
from aac.execute.plugin_runner import AacCommandArgument, AacCommand

class TestAacCommandArgument(unittest.TestCase):
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

class TestAacCommand(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()