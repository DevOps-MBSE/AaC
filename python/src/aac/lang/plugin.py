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
    description: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    commands: list[PluginCommand] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    definition_sources: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        description = None
        if "description" in data:
            description = data.pop("description")
        commands_data = data.pop("commands", [])
        commands = [PluginCommand.from_dict(command_data) for command_data in commands_data]
        definition_sources = data.pop("definition_sources", [])
        return cls(description=description, commands=commands, definition_sources=definition_sources, **data)

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("Plugin must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "name" not in structure:
    #             raise LanguageError("Plugin must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "description" in structure:
    #             self.description = structure["description"]
    #         else:
    #             self.description = ""
    #         if "commands" in structure:
    #             self.commands = []
    #             for command in structure["commands"]:
    #                 self.commands.append(PluginCommand(structure=command))
    #         else:
    #             self.commands = []
    #         if "definition_sources" in structure:
    #             self.definition_sources = structure["definition_sources"]
    #         else:
    #             self.definition_sources = []
    #     else:
    #         if "name" not in kwargs:
    #             raise LanguageError("Plugin must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "description" in kwargs:
    #             self.description = kwargs["description"]
    #         else:
    #             self.description = ""
    #         if "commands" not in kwargs:
    #             raise LanguageError("Plugin must have commands")
    #         else:
    #             self.commands = kwargs["commands"]
    #         if "definition_sources" not in kwargs:
    #             raise LanguageError("Plugin must have definition_sources")
    #         else:
    #             self.definition_sources = kwargs["definition_sources"]

    @staticmethod
    def get_gen_plugin_template() -> str:
        return get_resource_file_contents(__package__, "templates/plugin.jinja2")

    