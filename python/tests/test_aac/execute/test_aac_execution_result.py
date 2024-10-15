import unittest
from aac.execute.aac_execution_result import ExecutionResult, ExecutionMessage, ExecutionStatus, MessageLevel

class TestExecitionResult(unittest.TestCase):

    def test_execution_result(self):
        execution_result = ExecutionResult("name", "command_name", ExecutionStatus.GENERAL_FAILURE, [])
        execution_result.add_message("message 1")
        execution_result.add_messages([
            ExecutionMessage("message 2", MessageLevel.INFO, None, None),
            ExecutionMessage("message 3", MessageLevel.INFO, None, None),
            ])
        execution_result.status_code = ExecutionStatus.SUCCESS

        messages = execution_result.get_messages_as_string()
        print(messages)
        self.assertEqual(messages, "message 1\nmessage 2\nmessage 3\n")
        self.assertEqual(execution_result.status_code, ExecutionStatus.SUCCESS)

    def test_execution_result_no_message(self):
        with self.assertRaises(TypeError):
            execution_result = ExecutionResult("name", "command_name", None, None)


