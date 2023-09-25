from dataclasses import dataclass
from attr import attrib, validators, Factory
import attr
from typing import Optional
from aac.package_resources import get_resource_file_contents
from aac.execute.aac_execution_result import LanguageError
from aac.lang.plugincommand import PluginCommand


@dataclass(frozen=True)
class Project():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        return cls(description=description, **data)
    