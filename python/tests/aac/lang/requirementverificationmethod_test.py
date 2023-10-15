# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

import unittest
from aac.lang.requirementverificationmethod import RequirementVerificationMethod


class RequirementVerificationMethodTestHelper:
    @staticmethod
    def generate_data() -> str:
        return "ANALYSIS"

    @staticmethod
    def generate_data_required_only() -> str:
        return RequirementVerificationMethodTestHelper.generate_data()


class TestRequirementVerificationMethod(unittest.TestCase):
    def test_requirementverificationmethod_from_dict(self):
        self.assertEqual(
            RequirementVerificationMethod.from_dict("ANALYSIS"),
            RequirementVerificationMethod.ANALYSIS,
        )
        self.assertEqual(
            RequirementVerificationMethod.from_dict("DEMONSTRATION"),
            RequirementVerificationMethod.DEMONSTRATION,
        )
        self.assertEqual(
            RequirementVerificationMethod.from_dict("INSPECTION"),
            RequirementVerificationMethod.INSPECTION,
        )
        self.assertEqual(
            RequirementVerificationMethod.from_dict("TEST"),
            RequirementVerificationMethod.TEST,
        )

        with self.assertRaises(ValueError):
            RequirementVerificationMethod.from_dict("NEVER_GONNA_BE_A_VALID_ENUM_VALUE")


if __name__ == "__main__":
    unittest.main()