from dataclasses import dataclass
from attr import attrib, validators, Factory
import attr
from typing import Optional
from aac.lang.projectdependency import ProjectDependency


@dataclass(frozen=True)
class SchemaExtension():
    
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    