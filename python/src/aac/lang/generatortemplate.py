from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError
from aac.lang.generatordatasource import GeneratorDataSource

@dataclass(frozen=True)
class GeneratorTemplate():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    gen_from: GeneratorDataSource = attrib(init=attr.ib(), validator=validators.instance_of(GeneratorDataSource))
    template_file: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    template_contents: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        gen_from = GeneratorDataSource.from_dict(data.pop("gen_from"))
        template_file = None
        if "template_file" in data:
            template_file = data.pop("template_file")
        template_contents = None
        if "template_contents" in data:
            template_contents = data.pop("template_contents")
        return cls(description=description, gen_from=gen_from, template_file=template_file, template_contents=template_contents, **data)
