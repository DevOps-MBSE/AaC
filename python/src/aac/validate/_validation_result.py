from attr import attrib, attrs, validators, Factory


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of the validation of a single definition.

    Attributes:
        parsed_definitions (list): Parsed definitions that were part of the validated content
        messages (list): A dictionary of definition names as keys to lists of messages
        is_valid (bool): A bool indicating whether the definition is valid or not (True/False)
    """

    parsed_definitions: list = attrib(validator=validators.instance_of(list))
    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    is_valid: bool = attrib(default=False, validator=validators.instance_of(bool))
