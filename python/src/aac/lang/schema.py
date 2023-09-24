from dataclasses import dataclass
import attr
from typing import Optional
import attr
from attr import attrib, validators, Factory
from aac.execute.aac_execution_result import LanguageError
from aac.lang.aactype import AacType
from aac.lang.field import Field
from aac.package_resources import get_resource_file_contents

@dataclass(frozen=True)
class Schema(AacType):

    extends: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    modifiers: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    root: Optional[str] = attrib(default=None, init=attr.ib(), validator=validators.optional(validators.instance_of(str))) 
    gen_plugin_template_file: Optional[str] = attrib(default=None, init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    fields: list[Field] = attrib(default=Factory(list), init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        extends = []
        if "extends" in data:
            extends = data.pop("extends")
        modifiers = []
        if "modifiers" in data:
            modifiers = data.pop("modifiers")
        root = None
        if "root" in data:
            root = data.pop("root")
        gen_plugin_template_file = None
        if "gen_plugin_template_file" in data:
            gen_plugin_template_file = data.pop("gen_plugin_template_file")
        fields_data = data.pop("fields", [])
        fields = [Field.from_dict(field_data) for field_data in fields_data]
        return cls(extends=extends,root=root, gen_plugin_template_file=gen_plugin_template_file, modifiers=modifiers, fields=fields, **data)

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

    