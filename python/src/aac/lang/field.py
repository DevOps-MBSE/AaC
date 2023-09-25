from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class Field():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    type: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    is_required: bool = attrib(init=attr.ib(), validator=validators.instance_of(bool))
    default: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        is_required = False
        if "is_required" in data:
            is_required = data.pop("is_required")
        default = None
        if "default" in data:
            default = data.pop("default")
        return cls(description=description, is_required=is_required, default=default, **data)
