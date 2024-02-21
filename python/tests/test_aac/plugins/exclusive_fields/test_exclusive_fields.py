from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_context import LanguageContext
from os import linesep


from aac.plugins.exclusive_fields.exclusive_fields_impl import plugin_name


from aac.plugins.exclusive_fields.exclusive_fields_impl import mutually_exclusive_fields


class TestExclusiveFields(TestCase):
    def test_mutually_exclusive_fields(self):
        
        context = LanguageContext()
        one_definition = context.parse_and_load(TEST_EXCLUSIVE_FIELDS)

        # good data tests
        for good_def in [GOOD_DATA_1, GOOD_DATA_2, GOOD_DATA_3]:
            good = context.parse_and_load(good_def)
            result = mutually_exclusive_fields(good[0].instance, one_definition[0], None, ["alpha", "beta", "gamma"])
            self.assertTrue(result.is_success(), f"Expected success for {good[0].name}")
            context.remove_definitions(good)

        # bad data tests
        for bad_def in [BAD_DATA_1, BAD_DATA_2, BAD_DATA_3, BAD_DATA_4]:
            bad = context.parse_and_load(bad_def)
            result = mutually_exclusive_fields(bad[0].instance, one_definition[0], None, ["alpha", "beta", "gamma"])
            self.assertFalse(result.is_success(), f"Expected failure for {bad[0].name}")
            context.remove_definitions(bad)

        context.remove_definitions(one_definition)

TEST_EXCLUSIVE_FIELDS = """
schema:
    name: One
    package: test.exclusive_fields
    root: one
    fields:
        - name: name
          type: string
          is_required: true
        - name: alpha
          type: string
        - name: beta
          type: string
        - name: gamma
          type: string
    constraints:
        - name: Mutually exclusive fields
          arguments:
            fields:
                - alpha
                - beta
                - gamma  

"""

GOOD_DATA_1 = """
one:
    name: GoodOne
    alpha: alpha
"""

GOOD_DATA_2 = """
one:
    name: GoodTwo
    beta: beta
"""

GOOD_DATA_3 = """
one:
    name: GoodThree
    gamma: gamma
"""

BAD_DATA_1 = """
one:
    name: bad
    alpha: alpha
    beta: beta
"""

BAD_DATA_2 = """
one:
    name: bad
    alpha: alpha
    gamma: gamma
"""

BAD_DATA_3 = """
one:
    name: bad
    beta: beta
    gamma: gamma
"""

BAD_DATA_4 = """
one:
    name: bad
    alpha: alpha
    beta: beta
    gamma: gamma
"""