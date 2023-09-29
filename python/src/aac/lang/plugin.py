from dataclasses import dataclass
from attr import attrib, validators, Factory
import attr
from typing import Optional
from aac.package_resources import get_resource_file_contents
from aac.execute.aac_execution_result import LanguageError
from aac.lang.plugincommand import PluginCommand


@dataclass(frozen=True)
class Plugin():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    package: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    commands: list[PluginCommand] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    definition_sources: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        commands_data = data.pop("commands", [])
        print(f"DEBUG:  Plugin constructure found commands_data = \n{commands_data}")
        commands_list = [PluginCommand.from_dict(command_data) for command_data in commands_data]
        print(f"DEBUG:  Plugin constructure - commands_list = \n{commands_list}")
        definition_sources = data.pop("definition_sources", [])
        return cls(description=description, commands=commands_list, definition_sources=definition_sources, **data)
    