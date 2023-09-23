from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.cli.aac_execution_result import LanguageError

@dataclass(frozen=True)
class Field():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    type: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    is_required: Optional[bool] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(bool)))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise Exception("Field must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "name" not in structure:
    #             raise Exception("Field must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "type" not in structure:
    #             raise Exception("Field must have a type")
    #         else:
    #             self.type = structure["type"]
    #         if "description" in structure:
    #             self.description = structure["description"]
    #         else:
    #             self.description = ""
    #         if "is_required" in structure:
    #             self.is_required = bool(structure["is_required"])
    #         else:
    #             self.is_required = False
    #     else:
    #         if "name" not in kwargs:
    #             raise LanguageError("Field must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "type" not in kwargs:
    #             raise LanguageError("Field must have a type")
    #         else:
    #             self.type = kwargs["type"]
    #         if "description" in kwargs:
    #             self.description = kwargs["description"]
    #         else:
    #             self.description = ""
    #         if "is_required" in kwargs:
    #             self.is_required = kwargs["is_required"]
    #         else:
    #             self.is_required = False
        