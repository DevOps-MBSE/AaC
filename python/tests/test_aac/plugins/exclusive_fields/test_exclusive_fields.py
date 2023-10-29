from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.exclusive_fields.exclusive_fields_impl import plugin_name


from aac.plugins.exclusive_fields.exclusive_fields_impl import mutually_exclusive_fields


class TestExclusivefields(TestCase):
    def test_mutually_exclusive_fields(self):
        # TODO: Write tests for mutually_exclusive_fields
        self.fail("Test not yet implemented.")
