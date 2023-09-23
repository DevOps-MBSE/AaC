from dataclasses import dataclass
from aac.lang.aactype import AacType
import attr
from typing import Optional
from attr import attrib, validators

@dataclass(frozen=True)
class Primitive(AacType):

    python_type: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("Primitive must be initialized with keyword arguments")
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         super(args, kwargs)
    #         if "python_type" in structure:
    #             self.python_type = structure["python_type"]
    #         else:
    #             raise LanguageError("Primitive must have python_type")
    #     else:
    #         super(args, kwargs)
    #         if "python_type" in kwargs:
    #             self.python_type = kwargs["python_type"]
    #         else:
    #             raise LanguageError("Primitive must have python_type")
