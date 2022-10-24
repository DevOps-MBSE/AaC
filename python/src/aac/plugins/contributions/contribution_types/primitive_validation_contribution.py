"""Type Validation Contribution class."""
from __future__ import annotations
from attr import attrib, attrs, validators


@attrs(hash=False)
class PrimitiveValidationContribution:
    """
    A class that contains all the relevant information to manage and execute type validator contributions against type-value enums in the validation process.

    Attributes:
        name: The name of the enum validator
        primitive_type: The enum type
        validation_function: The validation callback function
    """

    name: str = attrib(validator=validators.instance_of(str))
    primitive_type: str = attrib(validator=validators.instance_of(str))
    validation_function: callable = attrib(validator=validators.is_callable())

    def __hash__(self) -> int:
        """Return the hash of this TypeValidationContribution."""
        return hash(self.name)
