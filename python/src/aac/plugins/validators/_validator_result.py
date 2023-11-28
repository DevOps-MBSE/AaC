"""A module for representing validator results."""
from attr import Factory, attrib, attrs, validators

from aac.lang.definitions.definition import Definition
from aac.plugins.validators._validator_finding import ValidatorFinding
from aac.plugins.validators._validator_findings import ValidatorFindings
from typing import Optional


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

    def is_valid(self, fail_on_warning: Optional[bool] = False) -> bool:
        error_count = len(self.findings.get_error_findings())
        warning_count = len(self.findings.get_warning_findings())
        if (fail_on_warning):
            # Return True if there are no warning or error messages on the validation result; False, otherwise.
            result = (warning_count + error_count == 0)
        else:
            # Return True if there are no error messages on the validation result; False, otherwise.
            result = (error_count == 0)
        return result

    def get_messages_as_string(self) -> str:
        """Get all of the validator result messages as a single string."""

        def format_message(finding: ValidatorFinding) -> str:
            loc = finding.location
            return (
                f"\nValidation {finding.severity.name} from '{loc.validation_name}' in {loc.source.uri} "
                f"at {loc.location.line + 1}:{loc.location.column} {finding.message}"
            )

        valid_files_output = ""

        if self.is_valid():
            definition_sources = []
            for definition in self.definitions:
                if definition.source.uri not in definition_sources:
                    definition_sources.append(definition.source.uri)

            valid_files_output = "\nThe following additional definition files have been validated:\n" + "\n".join(definition_file for definition_file in definition_sources)

        return f"{valid_files_output}\n" + "\n".join([format_message(finding) for finding in self.findings.get_all_findings()])
