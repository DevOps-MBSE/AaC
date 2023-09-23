from dataclasses import dataclass
from aac.lang.aactype import AacType
from aac.package_resources import get_resource_file_contents

@dataclass(frozen=True)
class Primitive(AacType):
    
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/primitive.jinja2")
