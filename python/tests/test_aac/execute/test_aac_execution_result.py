from unittest import TestCase
from aac.execute.aac_execution_result import ExecutionResult, ExecutionMessage, ExecutionStatus, MessageLevel

class TestExecitionResult(TestCase):

    def test_execution_result(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.GENERAL_FAILURE, [])
        execution_result.add_messages([
            ExecutionMessage("message 1", MessageLevel.DEBUG, None, None),
            ExecutionMessage("message 2", MessageLevel.INFO, None, None),
            ExecutionMessage("message 3", MessageLevel.WARNING, None, None),
            ExecutionMessage("message 4", MessageLevel.ERROR, None, None)
            ])
        execution_result.status_code = ExecutionStatus.SUCCESS

        messages = execution_result.get_messages_as_string()
        self.assertEqual(messages, "message 1\nmessage 2\nmessage 3\nmessage 4\n")
        messages_list = execution_result.messages
        self.assertEqual(messages_list[0].level, MessageLevel.DEBUG)
        self.assertEqual(messages_list[1].level, MessageLevel.INFO)
        self.assertEqual(messages_list[2].level, MessageLevel.WARNING)
        self.assertEqual(messages_list[3].level, MessageLevel.ERROR)
        self.assertTrue(execution_result.is_success)

    def test_status_enum(self):
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

    def test_execution_result_no_message(self):
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", "command_name", ExecutionStatus.SUCCESS, [])
            execution_result.add_message("message")


