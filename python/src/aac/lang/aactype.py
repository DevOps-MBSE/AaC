from dataclasses import dataclass
from abc import ABC
import attr
from typing import Optional
from attr import attrib, validators

@dataclass(frozen=True)
class AacType(ABC):
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    @classmethod
    def from_dict(cls, data: dict):
        description = None
        if "description" in data:
            description = data.pop("description")
        return cls(description=description, **data)
        