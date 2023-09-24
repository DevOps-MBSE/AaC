from dataclasses import dataclass
from attr import attrib, validators
import attr
from aac.lang.aactype import AacType
from aac.package_resources import get_resource_file_contents
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class AacEnum(AacType):

    values: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("AacEnum must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         super(args, kwargs)
            
    #         if "values" in structure:
    #             self.values = structure["values"]
    #         else:
    #             raise LanguageError("AacEnum must have values")
    #     else:
    #         super(args, kwargs)
    #         if "values" not in kwargs:
    #             raise LanguageError("AacEnum must have values")
    #         else:
    #             self.values = kwargs["values"]

    
    @staticmethod
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/enum.jinja2")
