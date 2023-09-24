from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators, Factory
import attr
from aac.execute.aac_execution_result import LanguageError
from aac.lang.field import Field

@dataclass(frozen=True)
class Modifier():

    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    fields: Optional[list[Field]] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        fields_data = data.pop("fields", [])
        fields = [Field.from_dict(field_data) for field_data in fields_data]
        return cls(description=description, fields=fields, **data)
    
    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("Modifier must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         super(args, kwargs)
    #         if "name" not in structure:
    #             raise LanguageError("Modifier must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "description" in structure:
    #             self.description = structure["description"]
    #         else:
    #             self.description = ""
    #         if "fields" in structure:
    #             self.fields = structure["fields"]
    #         else:
    #             self.fields = []
    #     else:
    #         if "name" not in kwargs:
    #             raise LanguageError("Modifier must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "description" in kwargs:
    #             self.description = kwargs["description"]
    #         else:
    #             self.description = ""
    #         if "fields" not in kwargs:
    #             self.fields = []
    #         else:
    #             self.fields = kwargs["fields"]
