from dataclasses import dataclass
from aac.lang.aactype import AacType
from aac.lang.field import Field
from aac.package_resources import get_resource_file_contents

@dataclass(frozen=True)
class Schema(AacType):
    extends: list[str]
    modifiers: list[str]
    fields: list[Field]

    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/schema.jinja2")

    