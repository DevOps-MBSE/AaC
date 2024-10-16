from unittest import TestCase
from aac.execute.aac_execution_result import ExecutionResult, ExecutionMessage, ExecutionStatus, MessageLevel


class TestExecutionResult(TestCase):

    def test_execution_result_name(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
        self.assertEqual(execution_result.plugin_name, "name")
        self.assertEqual(execution_result.plugin_command_name, "command_name")

    def test_execution_result_messages(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
        execution_result.add_messages([
            ExecutionMessage("message 1", MessageLevel.INFO, None, None),
            ExecutionMessage("message 2", MessageLevel.INFO, None, None),
            ExecutionMessage("message 3", MessageLevel.INFO, None, None),
            ExecutionMessage("message 4", MessageLevel.INFO, None, None)
        ])

        messages = execution_result.get_messages_as_string()
        self.assertEqual(messages, "message 1\nmessage 2\nmessage 3\nmessage 4\n")

    def test_execution_result_message_levels(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
        execution_result.add_messages([
            ExecutionMessage("message 1", MessageLevel.DEBUG, None, None),
            ExecutionMessage("message 2", MessageLevel.INFO, None, None),
            ExecutionMessage("message 3", MessageLevel.WARNING, None, None),
            ExecutionMessage("message 4", MessageLevel.ERROR, None, None)
        ])
        messages_list = execution_result.messages
        self.assertEqual(messages_list[0].level, MessageLevel.DEBUG)
        self.assertEqual(messages_list[1].level, MessageLevel.INFO)
        self.assertEqual(messages_list[2].level, MessageLevel.WARNING)
        self.assertEqual(messages_list[3].level, MessageLevel.ERROR)

    def test_execution_result_status_code(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.GENERAL_FAILURE, [])
        self.assertFalse(execution_result.is_success())
        execution_result.status_code = ExecutionStatus.SUCCESS
        self.assertTrue(execution_result.is_success())

    def test_execution_result_status_enum(self):
        execution_success = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
        execution_constraint_failure = ExecutionResult("name", "command_name", ExecutionStatus.CONSTRAINT_FAILURE, [])
        execution_constraint_warning = ExecutionResult("name", "command_name", ExecutionStatus.CONSTRAINT_WARNING, [])
        execution_parser_failure = ExecutionResult("name", "command_name", ExecutionStatus.PARSER_FAILURE, [])
        execution_plugin_failure = ExecutionResult("name", "command_name", ExecutionStatus.PLUGIN_FAILURE, [])
        execution_operation_cancelled = ExecutionResult("name", "command_name", ExecutionStatus.OPERATION_CANCELLED, [])
        execution_general_failure = ExecutionResult("name", "command_name", ExecutionStatus.GENERAL_FAILURE, [])

        self.assertEqual(execution_success.status_code, ExecutionStatus.SUCCESS)
        self.assertEqual(execution_constraint_failure.status_code, ExecutionStatus.CONSTRAINT_FAILURE)
        self.assertEqual(execution_constraint_warning.status_code, ExecutionStatus.CONSTRAINT_WARNING)
        self.assertEqual(execution_parser_failure.status_code, ExecutionStatus.PARSER_FAILURE)
        self.assertEqual(execution_plugin_failure.status_code, ExecutionStatus.PLUGIN_FAILURE)
        self.assertEqual(execution_operation_cancelled.status_code, ExecutionStatus.OPERATION_CANCELLED)
        self.assertEqual(execution_general_failure.status_code, ExecutionStatus.GENERAL_FAILURE)

    def test_execution_result_message_levels_invalid(self):
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
            execution_result.add_message("message", "INFO", None, None)
        with self.assertRaises(AttributeError):
            execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
            execution_result.add_message("message", MessageLevel.info, None, None)

    def test_execution_result_invalid_name(self):
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult(123, "command_name", ExecutionStatus.GENERAL_FAILURE, [])  # noqa: F841
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", 456, ExecutionStatus.GENERAL_FAILURE, [])  # noqa: F841

    def test_execution_result_invalid_status(self):
        with self.assertRaises(AttributeError):
            execution_result = ExecutionResult("name", "command_name", ExecutionStatus.general_failure, [])  # noqa: F841
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", "command_name", "general_failure", [])  # noqa: F841

    def test_execution_result_no_message(self):
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
            execution_result.add_message("message")
