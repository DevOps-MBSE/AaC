from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus, ExecutionResult
from aac.context.language_context import LanguageContext


from aac.plugins.constraint_assignment_arguments.constraint_assignment_arguments_impl import (
    plugin_name,
)


from aac.plugins.constraint_assignment_arguments.constraint_assignment_arguments_impl import (
    check_arguments_against_constraint_definition,
)


class TestConstraintAssignmentArguments(TestCase):
    def test_check_arguments_against_constraint_definition(self):
        
        context = LanguageContext()

        schema_constraint = context.get_definitions_by_name("SchemaConstraint")[0]
        if_true_then_empty = schema_constraint.instance.constraints[0]

        if not if_true_then_empty:
            self.fail("Expected if_true_then_empty to be defined but it was not.")

        result: ExecutionResult = check_arguments_against_constraint_definition(if_true_then_empty, schema_constraint, None)

        self.assertTrue(result.is_success(), f"Expected success but failed with message: {result.messages}")
