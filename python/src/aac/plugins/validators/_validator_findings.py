"""A module that facilitates working with a collection of validator findings."""

from attr import Factory, attrib, attrs, validators

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.validators._validator_finding import FindingLocation, FindingSeverity, ValidatorFinding


@attrs
class ValidatorFindings:
    """
    A collection of validator findings.

    Attributes:
        findings: A collection of validator findings.
    """

    findings: list[ValidatorFinding] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def add_findings(self, new_findings: list[ValidatorFinding]) -> None:
        """Add the new findings to the collection of all findings."""
        self.findings.extend(new_findings)

    def add_error_finding(self, definition: Definition, message: str, validation_name: str, lexeme: Lexeme) -> None:
        """Add the finding as an error finding."""
        self._add_finding_with_severity(definition, message, FindingSeverity.ERROR, validation_name, lexeme)

    def add_warning_finding(self, definition: Definition, message: str, validation_name: str, lexeme: Lexeme) -> None:
        """Add the finding as an warning finding."""
        self._add_finding_with_severity(definition, message, FindingSeverity.WARNING, validation_name, lexeme)

    def add_info_finding(self, definition: Definition, message: str, validation_name: str, lexeme: Lexeme) -> None:
        """Add the finding as an info finding."""
        self._add_finding_with_severity(definition, message, FindingSeverity.INFO, validation_name, lexeme)

    def _add_finding_with_severity(
        self, definition: Definition, message: str, severity: FindingSeverity, validation_name: str, lexeme: Lexeme
    ) -> None:
        location = FindingLocation.from_lexeme(validation_name, lexeme)
        self.add_findings([ValidatorFinding(definition, severity, message, location)])

    def get_all_findings(self) -> list[ValidatorFinding]:
        """Return a list of all the validator findings."""
        return self.findings

    def get_error_findings(self) -> list[ValidatorFinding]:
        """Return a list of error findings."""
        return self._get_findings_with_severity(FindingSeverity.ERROR)

    def get_warning_findings(self) -> list[ValidatorFinding]:
        """Return a list of warning findings."""
        return self._get_findings_with_severity(FindingSeverity.WARNING)

    def get_info_findings(self) -> list[ValidatorFinding]:
        """Return a list of info findings."""
        return self._get_findings_with_severity(FindingSeverity.INFO)

    def _get_findings_with_severity(self, severity: FindingSeverity) -> list[ValidatorFinding]:
        """Return a list of findings of the specified severity."""
        return [finding for finding in self.findings if finding.severity == severity]
