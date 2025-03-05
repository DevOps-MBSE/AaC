from unittest import TestCase
from aac.context.language_context import LanguageContext
from aac.plugins.exclusive_fields.exclusive_fields_impl import mutually_exclusive_fields


class TestExclusiveFields(TestCase):
    def test_mutually_exclusive_fields(self):

        context = LanguageContext()
        one_definition = context.parse_and_load(TEST_EXCLUSIVE_FIELDS)

        # good data tests
        for good_def in [GOOD_DATA_1, GOOD_DATA_2, GOOD_DATA_3, GOOD_DATA_4, GOOD_DATA_5, GOOD_DATA_6]:
            good = context.parse_and_load(good_def)
            result = mutually_exclusive_fields(good[0].instance, one_definition[0], None, ["alpha", "beta", "gamma"])
            self.assertTrue(result.is_success(), msg=f"Expected success for {good[0].name}")
            context.remove_definitions(good)

        # bad data tests
        for bad_def in [BAD_DATA_1, BAD_DATA_2, BAD_DATA_3, BAD_DATA_4, BAD_DATA_5, BAD_DATA_6]:
            bad = context.parse_and_load(bad_def)
            result = mutually_exclusive_fields(bad[0].instance, one_definition[0], None, ["alpha", "beta", "gamma"])
            self.assertFalse(result.is_success(), msg=f"Expected failure for {bad[0].name}")
            self.assertEqual(result.messages[0].source, "No file to reference")
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

GOOD_DATA_4 = """
one:
    name: GoodFour
    alpha: alpha
    alpha: alpha  #  Name & field argument duplication is OK
"""

GOOD_DATA_5 = """
one:
    name: GoodFive
    alpha: beta
"""

GOOD_DATA_6 = """
one:
    name: GoodSix
    alpha: beta
    alpha: gamma
"""

BAD_DATA_1 = """
one:
    name: BadOne
    alpha: alpha
    beta: beta
"""

BAD_DATA_2 = """
one:
    name: BadTwo
    alpha: alpha
    gamma: gamma
"""

BAD_DATA_3 = """
one:
    name: BadThree
    beta: beta
    gamma: gamma
"""

BAD_DATA_4 = """
one:
    name: BadFour
    alpha: alpha
    beta: beta
    gamma: gamma
"""

BAD_DATA_5 = """
one:
    name: BadSix
    beta: beta
    alpha: alpha
"""

BAD_DATA_6 = """
one:
    name: BadEight
    alpha: beta
    beta: gamma
"""
