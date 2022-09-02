from typing import Optional
from unittest import TestCase
from aac.lang.definitions.definition import Definition

from aac.plugins.validators._validator_finding import FindingSeverity, ValidatorFinding
from aac.plugins.validators._validator_findings import ValidatorFindings

from tests.helpers.parsed_definitions import create_schema_definition


DEFAULT_TEST_DEFINITION: Definition = create_schema_definition("Test")
DEFAULT_TEST_FINDINGS: list[ValidatorFinding] = [
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.ERROR, "test error finding"),
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.WARNING, "test warning finding"),
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.INFO, "test info finding"),
]


class TestValidatorFindings(TestCase):
    def test_add_findings_of_specific_severity(self):
        validator_findings = self.get_validator_findings()

        self.assertEqual(len(validator_findings.get_all_findings()), len(DEFAULT_TEST_FINDINGS))

    def test_get_findings(self):
        validator_findings = self.get_validator_findings()

        self.assertListEqual(DEFAULT_TEST_FINDINGS, validator_findings.get_all_findings())

    def test_get_findings_of_specific_severity(self):
        validator_findings = self.get_validator_findings()

        self.assertEqual(len(validator_findings.get_error_findings()), 1)
        self.assertEqual(len(validator_findings.get_warning_findings()), 1)
        self.assertEqual(len(validator_findings.get_info_findings()), 1)

    def get_validator_findings(
        self, validator_findings: Optional[ValidatorFindings] = None, findings: list[ValidatorFinding] = DEFAULT_TEST_FINDINGS,
    ) -> ValidatorFindings:
        validator_findings = validator_findings or ValidatorFindings()
        self.assertEqual(len(validator_findings.get_all_findings()), 0)

        validator_findings.add_findings(findings)
        self.assertEqual(len(validator_findings.get_all_findings()), len(findings))

        return validator_findings
