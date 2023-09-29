from dataclasses import dataclass
import attr
from typing import Optional
from attr import attrib, validators
from aac.execute.aac_execution_result import LanguageError
from aac.lang.generatoroutputtarget import GeneratorOutputTarget
from aac.lang.overwriteoption import OverwriteOption
from aac.lang.jinjahelperfunction import JinjaHelperFunction

@dataclass(frozen=True)
class GeneratorTemplate():
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    template_file: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    overwrite: OverwriteOption = attrib(init=attr.ib(), validator=validators.instance_of(OverwriteOption))
    helper_functions: list[JinjaHelperFunction] = attrib(init=attr.ib(), validator=validators.instance_of(list[JinjaHelperFunction]))
    output_target: GeneratorOutputTarget = attrib(init=attr.ib(), validator=validators.instance_of(GeneratorOutputTarget))
    output_path_uses_data_source_package: bool = attrib(init=attr.ib(), validator=validators.instance_of(bool))
    output_file_prefix: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    output_file_name: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    output_file_suffix: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    output_file_extension: str = attrib(init=attr.ib(), validator=validators.instance_of(str))

    @classmethod
    def from_dict(cls, data):
        print(f"DEBUG: GeneratorTemplate.from_dict: data: {data}")
        description = None
        if "description" in data:
            description = data.pop("description")
        helper_functions = []
        if "helper_functions" in data:
            helper_functions = [JinjaHelperFunction.from_dict(helper_function) for helper_function in data.pop("helper_functions")]
        overwrite = OverwriteOption.from_dict(data.pop("overwrite"))
        output_file_prefix = None
        if "output_file_prefix" in data:
            output_file_prefix = data.pop("output_file_prefix")
        output_file_name = None
        if "output_file_name" in data:
            output_file_name = data.pop("output_file_name")
        output_file_suffix = None
        if "output_file_suffix" in data:
            output_file_suffix = data.pop("output_file_suffix")
        output_target = GeneratorOutputTarget.from_dict(data.pop("output_target"))
        return cls(description=description, helper_functions=helper_functions,overwrite=overwrite, output_file_prefix=output_file_prefix, output_target=output_target, output_file_name=output_file_name, output_file_suffix=output_file_suffix, **data)
