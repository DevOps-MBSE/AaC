"""Validator_Plugin class."""
from __future__ import annotations
from attr import attrib, attrs, validators


@attrs
class Validator_Plugin:
    """
    A class that contains all the relevant information to manage and execute validator plugins with the validation process.

    Attributes:
        name: A string with the name of the command argument
        validation_definition: The AaC definition of the Validator Plugin
        validation_function:
        validation_arguments:
    """

    name = attrib(validator=validators.instance_of(str))
    validation_definition = attrib(validator=validators.instance_of(str))
    validation_function = attrib(validator=validators.instance_of(callable))
    validation_arguments = attrib(default=None, validator=validators.instance_of((list, type(None))))

    @staticmethod
    def from_definition(validation_definition: dict) -> Validator_Plugin:
        new_validator_plugin = Validator_Plugin()
        new_validator_plugin.name = "Name"
        new_validator_plugin.validation_definition = "definition"
        return new_validator_plugin
