from unittest import TestCase
from aac.context.language_context import LanguageContext

from aac.plugins.if_true_then_empty.if_true_then_empty_impl import if_true_then_empty


class TestIfTrueThenEmpty(TestCase):
    def test_if_true_then_empty(self):
        
        context = LanguageContext()

        test_schema = context.parse_and_load(TEST_SCHEMA)

        for good in [GOOD_DATA_1, GOOD_DATA_2]:
            good_data = context.parse_and_load(good)
            result = if_true_then_empty(good_data[0].instance, test_schema[0], None, "alpha", "beta")
            self.assertTrue(result.is_success(), f"Expected success for {good_data[0].name}")
            context.remove_definitions(good_data)

        for bad in [BAD_DATA_1]:
            bad_data = context.parse_and_load(bad)
            result = if_true_then_empty(bad_data[0].instance, test_schema[0], None, "alpha", "beta")
            self.assertFalse(result.is_success(), f"Expected failure for {bad_data[0].name}")
            context.remove_definitions(bad_data)

        context.remove_definitions(test_schema)


TEST_SCHEMA = """
schema:
    name: IfTrueEmptyTest
    package: test.if_true_then_empty
    root: one
    fields:
        - name: name
          type: string
        - name: alpha
          type: bool
        - name: beta
          type: string[]
    constraints:
        - name: If true then empty
          arguments:
            - name: bool_field_name
              value: alpha
            - name: empty_field_name
              value: beta

"""

GOOD_DATA_1 = """
one:
    name: GoodData1
    alpha: true
"""

GOOD_DATA_2 = """
one:
    name: GoodData2
    alpha: false
    beta:
        - one
        - two
"""

BAD_DATA_1 = """
one:
    name: BadData1
    alpha: true
    beta:
        - one
        - two
"""
