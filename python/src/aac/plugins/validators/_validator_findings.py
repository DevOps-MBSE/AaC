"""A module that facilitates working with a collection of validator findings."""


from attr import Factory, attrib, attrs, validators

from aac.plugins.validators._validator_finding import FindingSeverity, ValidatorFinding


# QUESTION: Should we allow duplicate findings? Perhaps we can make that configurable if that's the
# desired behavior?
@attrs
class ValidatorFindings:
    """
    A collection of validator findings.

    Attributes:
        findings: A collection of validator findings.
    """

    findings: list[ValidatorFinding] = attrib(init=False, default=Factory(list), validator=validators.instance_of(list))

    def add_findings(self, new_findings: list[ValidatorFinding]) -> None:
        """Add the new findings to the collection of all findings."""
        self.findings.extend(new_findings)

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
