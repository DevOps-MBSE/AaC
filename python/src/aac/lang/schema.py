from dataclasses import dataclass
import attr
from typing import Optional
import attr
from attr import attrib, validators, Factory
from aac.execute.aac_execution_result import LanguageError
from aac.lang.aactype import AacType
from aac.lang.modifier import Modifier
from aac.lang.field import Field
from aac.package_resources import get_resource_file_contents

@dataclass(frozen=True)
class Schema(AacType):

    extends: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    modifiers: list[Modifier] = attrib(init=attr.ib(), validator=validators.instance_of(list))
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
            modifiers = [Modifier.from_dict(modifier_data) for modifier_data in modifiers]
        root = None
        if "root" in data:
            root = data.pop("root")
        fields_data = data.pop("fields", [])
        fields = [Field.from_dict(field_data) for field_data in fields_data]
        return cls(extends=extends,root=root, modifiers=modifiers, fields=fields, **data)
    