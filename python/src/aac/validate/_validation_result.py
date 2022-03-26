from attr import attrib, attrs, validators, Factory

from aac.parser.ParsedDefinition import ParsedDefinition


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of the validation of a single definition.

    Attributes:
        definition (ParsedDefinition): The definition that was validated
        messages (list): A dictionary of definition names as keys to lists of messages
        is_valid (bool): A bool indicating whether the definition is valid or not (True/False)
    """

    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    definition: ParsedDefinition = attrib(default=None, validator=validators.instance_of(ParsedDefinition))
    is_valid: bool = attrib(default=False, validator=validators.instance_of(bool))
