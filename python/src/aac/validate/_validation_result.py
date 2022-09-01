"""A module for representing the aggregated validation result."""

from typing import Callable

from attr import attrib, attrs, validators, Factory

from aac.plugins.validators._validator_findings import ValidatorFindings


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of the validation of a single definition.

    Attributes:
        findings (ValidatorFindings): A collection of findings that resulted from running validation
                                      on the Definition.
        is_valid (Callable): A function that accepts a ValidationResult and returns True if it
                             should be considered valid or False if it should be considered invalid.
    """

    def _is_valid_if_no_errors(self):
        """
        Return True if there are no error messages on the validation result; False, otherwise.

        This is a default implementation for determining if a ValidationResult is valid, or not.
        """
        return len(self.findings.get_error_findings()) == 0

    findings: ValidatorFindings = attrib(default=Factory(list), validator=validators.instance_of(list))
    is_valid: Callable = attrib(default=_is_valid_if_no_errors, validator=validators.is_callable())
