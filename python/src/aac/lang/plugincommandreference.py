from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators, Factory
import attr
from aac.execute.aac_execution_result import LanguageError
from aac.lang.field import Field

@dataclass(frozen=True)
class PluginCommandReference():

    plugin: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    command: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        
        return cls(**data)
    