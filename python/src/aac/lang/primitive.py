from dataclasses import dataclass
from aac.lang.aactype import AacType
import attr
from typing import Optional
from attr import attrib, validators

@dataclass(frozen=True)
class Primitive(AacType):

    python_type: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
