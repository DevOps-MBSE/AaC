from dataclasses import dataclass
from attr import attrib, validators
import attr
from aac.lang.aactype import AacType
from aac.package_resources import get_resource_file_contents
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class AacEnum(AacType):

    extends: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    values: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    
    @staticmethod
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/enum.jinja2")
