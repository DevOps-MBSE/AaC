"""ValidatorPlugin class."""
from __future__ import annotations
from attr import attrib, attrs, validators

from aac.parser import ParsedDefinition


@attrs
class ValidatorPlugin:
    """
    A class that contains all the relevant information to manage and execute validator plugins with the validation process.

    Attributes:
        name: A string with the name of the command argument
        definition: The AaC definition of the Validator Plugin
        validation_function: The validation callback function
        arguments: Any additional arguments to supply to the validation_function
    """

    name: str = attrib(validator=validators.instance_of(str))
    definition: ParsedDefinition = attrib(validator=validators.instance_of(ParsedDefinition))
    validation_function: callable = attrib(default=None, validator=validators.is_callable())
    arguments: dict = attrib(default={}, validator=validators.instance_of(dict))
