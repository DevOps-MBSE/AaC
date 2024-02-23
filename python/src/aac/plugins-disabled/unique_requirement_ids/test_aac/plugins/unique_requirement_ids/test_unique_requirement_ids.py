from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.unique_requirement_ids.unique_requirement_ids_impl import plugin_name


from aac.plugins.unique_requirement_ids.unique_requirement_ids_impl import (
    requirement_id_is_unique,
)


class TestUniqueRequirementIDs(TestCase):

    def test_requirement_id_is_unique(self):

        # TODO: Write success and failure tests for requirement_id_is_unique
        self.fail("Test not yet implemented.")
