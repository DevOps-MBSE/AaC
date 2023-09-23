from dataclasses import dataclass
from abc import ABC
import attr
from typing import Optional
from attr import attrib, validators

@dataclass(frozen=True)
class AacType(ABC):
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise Exception("AacType must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "name" not in structure:
    #             raise Exception("AacType must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "description" in structure:
    #             self.description = structure["description"]
    #         else:
    #             self.description = ""
    #     else:
    #         if "name" not in kwargs:
    #             raise Exception("AacType must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "description" in kwargs:
    #             self.description = kwargs["description"]
    #         else:
    #             self.description = ""

    @staticmethod
    def get_gen_plugin_template() -> str:
        return ""
        