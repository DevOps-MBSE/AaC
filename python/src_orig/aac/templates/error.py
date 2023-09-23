"""A module dedicated to defining template-related errors."""


from attr import attrib, attrs, validators


@attrs
class AacTemplateError(BaseException):
    """
    An error indicating some problem processing a template for AaC.

    Attributes:
        message (str): A message to display to the user.
    """

    message: str = attrib(validator=validators.instance_of(str))
