from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.cli.aac_execution_result import LanguageError
from aac.lang.aactype import AacType
from aac.lang.field import Field
from aac.package_resources import get_resource_file_contents

@dataclass(frozen=True)
class Schema(AacType):

    extends: Optional[list[str]] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    modifiers: Optional[list[str]] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    root: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str))) 
    gen_plugin_template_file: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    fields: list[Field] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("Schema must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         super(args, kwargs)
            
    #         if "extends" in structure:
    #             self.extends = structure["extends"]
    #         else:
    #             self.extends = []
            
    #         if "modifiers" in structure:
    #             self.modifiers = structure["modifiers"]
    #         else:
    #             self.modifiers = []
            
    #         if "package" in structure:
    #             self.package = structure["package"]
    #         else:
    #             raise LanguageError("Schema must have package")
            
    #         if "root" in structure:
    #             self.root = structure["root"]
    #         else:
    #             self.root = ""
            
    #         if "gen_plugin_template_file" in structure:
    #             self.gen_plugin_template_file = structure["gen_plugin_template_file"]
    #         else:
    #             self.gen_plugin_template_file = ""
            
    #         if "fields" in structure:
    #             self.fields = []
    #             for field in structure["fields"]:
    #                 self.fields.append(Field(structure=field))
    #         else:
    #             raise LanguageError("Schema must have fields")
    #     else:
    #         super(args, kwargs)
    #         if "extends" in kwargs:
    #             self.extends = kwargs["extends"]
    #         else:
    #             self.extends = []
            
    #         if "modifiers" in kwargs:
    #             self.modifiers = kwargs["modifiers"]
    #         else:
    #             self.modifiers = []
            
    #         if "package" in kwargs:
    #             self.package = kwargs["package"]
    #         else:
    #             raise LanguageError("Schema must have package")
            
    #         if "root" in kwargs:
    #             self.root = kwargs["root"]
    #         else:
    #             self.root = []
            
    #         if "gen_plugin_template_file" in kwargs:
    #             self.gen_plugin_template_file = kwargs["gen_plugin_template_file"]
    #         else:
    #             self.gen_plugin_template_file = ""
            
    #         if "fields" in kwargs:
    #             self.fields = kwargs["fields"]
    #         else:
    #             raise LanguageError("Schema must have fields")

    @staticmethod
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/schema.jinja2")

    