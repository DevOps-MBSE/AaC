"""Type Validation Contribution class."""

from __future__ import annotations

from typing import Callable, Optional

from attr import attrib, attrs, validators


@attrs(hash=False)
class PrimitiveValidationContribution:
    """
    A contribution for validating a primitive value.

    A class that contains all the relevant information to manage and execute type validator
    contributions against type-value enums in the validation process.

    Attributes:
        name (str): The name of the enum validator
        primitive_type (str): The enum type
        validation_function (Optional[Callable]): The validation callback function
    """

    name: str = attrib(validator=validators.instance_of(str))
    primitive_type: str = attrib(validator=validators.instance_of(str))
    validation_function: Optional[Callable] = attrib(validator=validators.optional(validators.is_callable()))

    def __hash__(self) -> int:
        """Return the hash of this TypeValidationContribution."""
        return hash(self.name)
