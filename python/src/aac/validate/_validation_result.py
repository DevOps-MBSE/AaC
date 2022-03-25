from attr import attrib, attrs, validators, Factory


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of validating a model.

    Attributes:
        messages (list[str]): A list of messages to be provided as feedback for the user.
        model (dict): The model that was validated; if the model is invalid, None.
    """

    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    model: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))
