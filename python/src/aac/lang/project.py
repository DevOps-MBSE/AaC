from dataclasses import dataclass
from attr import attrib, validators, Factory
import attr
from typing import Optional
from aac.lang.projectdependency import ProjectDependency


@dataclass(frozen=True)
class Project():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    uses: list[ProjectDependency] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        uses_data = data.pop("uses", [])
        uses = [ProjectDependency.from_dict(uses_entry) for uses_entry in uses_data]
        return cls(description=description, uses=uses, **data)
    