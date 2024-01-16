"""Custom ParserError class that represents errors encountered during the parsing process."""
from attr import Factory, attrib, attrs, validators
from typing import Optional
from yaml.error import YAMLError


@attrs
class ParserError(BaseException):
    """An error that represents a file that could not be parsed."""
    source: str = attrib(validator=validators.instance_of(str))
    errors: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    yaml_error: Optional[YAMLError] = attrib(default=None, validator=validators.optional(validators.instance_of(YAMLError)))
