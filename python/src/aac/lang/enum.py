from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError
from aac.lang.aactype import AacType

@dataclass(frozen=True)
class Enum(AacType):
    extends: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    values: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        extends = []
        if "extends" in data:
            extends = data.pop("extends")
        return cls(extends=extends, **data)
