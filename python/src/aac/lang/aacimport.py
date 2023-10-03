from dataclasses import dataclass
from attr import attrib, validators
import attr
from aac.execute.aac_execution_result import LanguageError

@dataclass(frozen=True)
class AacImport():

    files: list[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
