"""Validator_Plugin class"""
from attr import Factory, attrib, attrs, validators


@attrs
class Validator_Plugin:
    """
    A class that contains all the relevant information to manage and execute validator plugins with the validation process.

    Attributes:
        name: A string with the name of the command argument
        parent_definition:
        validation_function:
        validation_arguments:
    """

    name = attrib(validator=validators.instance_of(str))
    parent_definition = attrib(validator=validators.instance_of(str))
    validation_function = attrib(validator=validators.instance_of(callable))
    validation_arguments = attrib(default=None, validator=validators.instance_of((list, type(None))))
