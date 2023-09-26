from dataclasses import dataclass
from attr import attrib, validators
import attr

@dataclass(frozen=True)
class ProjectDependency():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    version: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    