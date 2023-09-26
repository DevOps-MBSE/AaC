from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError
from aac.lang.generatorsource import GeneratorSource

@dataclass(frozen=True)
class Generator():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    sources: list[GeneratorSource] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        sources_data = data.pop("commands", [])
        sources = [GeneratorSource.from_dict(source_data) for source_data in sources_data]
        return cls(description=description, sources=sources, **data)
