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
    validation_definition = attrib(validator=validators.instance_of(dict))
    validation_function = attrib(default=None, validator=validators.instance_of((type(callable), type(None))))
    validation_arguments = attrib(default=None, validator=validators.instance_of((list, type(None))))

    @staticmethod
    def from_definition(validation_definition: dict) -> Validator_Plugin:
        """
        Parse a validation definition and return a new instance of Validator_Plugin populated from the validation definition.

        Args:
            validation_definition: The definition used to populate the returned class instance

        Returns:
            A instance of Validator_Plugin
        """
        def is_validation_definition(definition):
            return "validation" in definition

        validation_definitions = list(filter(is_validation_definition, validation_definition.values()))

        if len(validation_definitions) != 1:
            raise RuntimeError(f"Expected one and only one validation defintion.\nValidation Definitions:\n{validation_definitions}")

        plugin_definition = validation_definitions[0].get("validation")
        plugin_name = plugin_definition.get("name")

        return Validator_Plugin(name=plugin_name, validation_definition=validation_definition)
