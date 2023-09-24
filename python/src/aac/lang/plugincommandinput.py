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

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise Exception("PluginCommandInput must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "name" not in structure:
    #             raise LanguageError("PluginCommandInput must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "description" in structure:
    #             self.description = structure["description"]
    #         else:
    #             self.description = ""
    #         if "type" in structure:
    #             self.type = structure["type"]
    #         else:
    #             self.type = ""
    #         if "default" in structure:
    #             self.default = structure["default"]
    #         else:
    #             self.default = ""
    #     else:
    #         if "name" not in kwargs:
    #             raise LanguageError("PluginCommandInput must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "description" in kwargs:
    #             self.description = kwargs["description"]
    #         else:
    #             self.description = ""
    #         if "type" in kwargs:
    #             self.type = kwargs["type"]
    #         else:
    #             self.type = ""
    #         if "default" in kwargs:
    #             self.default = kwargs["default"]
    #         else:
    #             self.default = ""
    