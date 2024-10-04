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


    def test_check_arguments_against_constraint_definition_fail(self):

        context = LanguageContext()
        context.parse_and_load(BAD_DATA)

        schema_constraint = context.get_definitions_by_name("SchemaConstraintBad")[0]
        exclusive_fields = schema_constraint.instance.constraints[0]

        if not exclusive_fields:
            self.fail("Expected exclusive_fields to be defined but it was not.")

        result: ExecutionResult = check_arguments_against_constraint_definition(exclusive_fields, schema_constraint, None)

        self.assertTrue(not result.is_success(), f"Expected failure with message: {result.messages}")
        self.assertEqual(result.messages[0].message, "The Check arguments against constraint definition constraint for Mutually exclusive fields failed because the constraint definition has a required argument named fields that was not found in the constraint assignment.")


BAD_DATA = """
schema:
  name: SchemaConstraintBad
  package: aac.lang
  description: |
    The definition of a schema constraint plugin.  Schema constraints perform
    checks against a defined structure within a model based on its schema definition.
    Defining a schema constraint allows for automated structural quality checks
    by running the 'aac check' command against your model.
  fields:
    - name: name
      type: string
      description: |
        The name of the schema constraint rule.
      is_required: true
    - name: description
      type: string
      description: |
        A high level description of the schema constraint rule.
    - name: universal
      type: bool
      description: |
        Indicates that the constraint should be applied to all schemas without explicit assignment.
        This is a convenience so that you don't have to directly assign the constraint to every schema.
        If not included or false, the constraint must be explicitly assigned to a schema.  But be aware
        that universal schema constraints cannot have input arguments.
      default: false
    - name: arguments
      type: Field[]
      description: |
        List of arguments for the constraint.
    - name: acceptance
      type: Feature[]
      description: |
        A list of acceptance test features that describe the expected behavior of the schema constraint.
  constraints:
    - name: Mutually exclusive fields
"""
