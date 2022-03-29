from attr import attrib, attrs, validators, Factory

from aac.parser import ParsedDefinition
from aac.plugins.validators import ValidatorPlugin


@attrs(slots=True, auto_attribs=True)
class ValidatorResult:
    """Represents the validation result from a validator plugin on a single definition.

    Attributes:
        validator (ValidatorPlugin): The originator of the validator result
        definition (ParsedDefinition): The definition that was validated
        messages (list): A dictionary of definition names as keys to lists of messages
        is_valid (bool): A bool indicating whether the definition is valid or not (True/False)
    """

    validator: ValidatorPlugin = attrib(default=None, validator=validators.instance_of(ValidatorPlugin))
    definition: ParsedDefinition = attrib(default=None, validator=validators.instance_of(ParsedDefinition))
    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    is_valid: bool = attrib(default=False, validator=validators.instance_of(bool))
