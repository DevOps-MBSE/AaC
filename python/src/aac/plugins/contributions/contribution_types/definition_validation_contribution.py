"""Rule Validation Contribution class."""

from __future__ import annotations

from typing import Callable, Optional

from attr import attrib, attrs, validators

from aac.lang.definitions.definition import Definition


@attrs(hash=False)
class DefinitionValidationContribution:
    """
    A contribution for validating a definition.

    A class that contains all the relevant information to manage and execute definition validation
    contributions with the validation process.

    Attributes:
        name (str): A string with the name of the command argument.
        definition (str): The AaC definition of the Validator Plugin.
        validation_function (Optional[Callable]): The validation callback function.
    """

    name: str = attrib(validator=validators.instance_of(str))
    definition: Definition = attrib(validator=validators.instance_of(Definition))
    validation_function: Optional[Callable] = attrib(validator=validators.optional(validators.is_callable()))

    def __hash__(self) -> int:
        """Return the hash of this DefinitionValidationContribution."""
        return hash(self.name)
