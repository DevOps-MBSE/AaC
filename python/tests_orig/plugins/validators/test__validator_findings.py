from typing import Optional
from unittest import TestCase
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation

from aac.plugins.validators._validator_finding import FindingLocation, FindingSeverity, ValidatorFinding
from aac.plugins.validators._validator_findings import ValidatorFindings

from tests.helpers.parsed_definitions import create_schema_definition


DEFAULT_TEST_DEFINITION: Definition = create_schema_definition("Test")
DEFAULT_FINDING_LOCATION: FindingLocation = FindingLocation("validate thing", DEFAULT_TEST_DEFINITION.source, 0, 0, 0, 0)
DEFAULT_TEST_FINDINGS: list[ValidatorFinding] = [
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.ERROR, "test error finding", DEFAULT_FINDING_LOCATION),
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.WARNING, "test warning finding", DEFAULT_FINDING_LOCATION),
    ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.INFO, "test info finding", DEFAULT_FINDING_LOCATION),
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

    def test_add_specific_findings(self):
        validator_findings = self.get_validator_findings(findings=[])
        lexeme = Lexeme(SourceLocation(0, 0, 0, 0), "<test>", "")

        error_message = "test error finding"
        error_finding = ValidatorFinding(
            DEFAULT_TEST_DEFINITION, FindingSeverity.ERROR, error_message, DEFAULT_FINDING_LOCATION
        )
        validator_findings.add_error_finding(DEFAULT_TEST_DEFINITION, error_message, "validate thing", lexeme)
        self.assertEqual(validator_findings.get_error_findings()[0], error_finding)

        warning_message = "test warning finding"
        warning_finding = ValidatorFinding(
            DEFAULT_TEST_DEFINITION, FindingSeverity.WARNING, warning_message, DEFAULT_FINDING_LOCATION
        )
        validator_findings.add_warning_finding(DEFAULT_TEST_DEFINITION, warning_message, "validate thing", lexeme)
        self.assertEqual(validator_findings.get_warning_findings()[0], warning_finding)

        info_message = "test info finding"
        info_finding = ValidatorFinding(DEFAULT_TEST_DEFINITION, FindingSeverity.INFO, info_message, DEFAULT_FINDING_LOCATION)
        validator_findings.add_info_finding(DEFAULT_TEST_DEFINITION, info_message, "validate thing", lexeme)
        self.assertEqual(validator_findings.get_info_findings()[0], info_finding)

    def get_validator_findings(
        self,
        validator_findings: Optional[ValidatorFindings] = None,
        findings: list[ValidatorFinding] = DEFAULT_TEST_FINDINGS,
    ) -> ValidatorFindings:
        validator_findings = validator_findings or ValidatorFindings()
        self.assertEqual(len(validator_findings.get_all_findings()), 0)

        validator_findings.add_findings(findings)
        self.assertEqual(len(validator_findings.get_all_findings()), len(findings))

        return validator_findings
