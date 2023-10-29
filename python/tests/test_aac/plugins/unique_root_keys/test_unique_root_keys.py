from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.unique_root_keys.unique_root_keys_impl import plugin_name


from aac.plugins.unique_root_keys.unique_root_keys_impl import root_key_names_are_unique


class TestUniqueRootKeys(TestCase):
    def test_root_key_names_are_unique(self):
        # TODO: Write tests for root_key_names_are_unique
        self.fail("Test not yet implemented.")
