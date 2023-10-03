from dataclasses import dataclass
from attr import attrib, validators
import attr
from aac.lang.aactype import AacType

@dataclass(frozen=True)
class AacEnum(AacType):

    extends: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    enumerated_values: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        extends = []
        if "extends" in data:
            extends = data.pop("extends")
        return cls(extends=extends, **data)
