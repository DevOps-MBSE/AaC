from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators
import attr
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class PluginCommandInput():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    type: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    default:  Optional[str] = attrib(default=None, init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        default = None
        if "default" in data:
            default = data.pop("default")
        return cls(description=description, default=default, **data)
