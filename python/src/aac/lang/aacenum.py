from dataclasses import dataclass
from aac.lang.aactype import AacType

@dataclass(frozen=True)
class AacEnum(AacType):
    
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/enum.jinja2")
