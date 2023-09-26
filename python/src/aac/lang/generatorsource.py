from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError
from aac.lang.generatortemplate import GeneratorTemplate

@dataclass(frozen=True)
class GeneratorSource():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    data_source: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    templates: list[GeneratorTemplate] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        templates_data = data.pop("commands", [])
        templates = [GeneratorTemplate.from_dict(template_data) for template_data in templates_data]
        return cls(templates=templates, **data)
