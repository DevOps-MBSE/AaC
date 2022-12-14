"""A module for representing validator results."""
from attr import Factory, attrib, attrs, validators

from aac.lang.definitions.definition import Definition
from aac.plugins.validators._validator_finding import ValidatorFinding
from aac.plugins.validators._validator_findings import ValidatorFindings


@attrs(slots=True)
class ValidatorResult:
    """
    Represents the result of the validation of one, or more, definitions.

    Attributes:
        definitions (list[Definition]): The list of definitions that were validated; they are
                                        valid if this result is valid.
        findings (ValidatorFindings): A collection of findings that resulted from running validation
                                      on the Definition.
    """

    definitions: list[Definition] = attrib(default=Factory(list), validator=validators.instance_of(list))
    findings: ValidatorFindings = attrib(
        default=Factory(ValidatorFindings), validator=validators.instance_of(ValidatorFindings)
    )

    def is_valid(self) -> bool:
        """Return True if there are no error messages on the validation result; False, otherwise."""
        return len(self.findings.get_error_findings()) == 0

    def get_messages_as_string(self) -> str:
        """Get all of the validator result messages as a single string."""

        def format_message(finding: ValidatorFinding) -> str:
            loc = finding.location
            return (
                f"\nValidation finding from '{loc.validation_name}' of level {finding.severity.name} in {loc.source.uri}. "
                f"Message:\n {finding.message}"
            )

        return "\n".join([format_message(finding) for finding in self.findings.get_all_findings()])
