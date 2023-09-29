from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class JinjaHelperFunction():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    module: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    function: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        return cls(description=description, **data)
