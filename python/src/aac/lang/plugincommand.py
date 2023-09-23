from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators
import attr
from aac.cli.aac_execution_result import LanguageError
from aac.lang.plugincommandinput import PluginCommandInput

@dataclass(frozen=True)
class PluginCommand():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    helpText: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    run_before: Optional[list[str]] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))
    run_after: Optional[list[str]] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))
    input: Optional[list[PluginCommandInput]] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("PluginCommand must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "name" not in structure:
    #             raise LanguageError("PluginCommand must have a name")
    #         else:
    #             self.name = structure["name"]
    #         if "helpText" in structure:
    #             self.helpText = structure["helpText"]
    #         else:
    #             self.helpText = ""
    #         if "run_before" in structure:
    #             self.run_before = structure["run_before"]
    #         else:
    #             self.run_before = []
    #         if "run_after" in structure:
    #             self.run_after = structure["run_after"]
    #         else:
    #             self.run_after = []
    #         if "input" in structure:
    #             self.input = []
    #             for input in structure["input"]:
    #                 self.input.append(PluginCommandInput(structure=input))
    #         else:
    #             self.input = []
    #     else:
    #         if "name" not in kwargs:
    #             raise LanguageError("PluginCommand must have a name")
    #         else:
    #             self.name = kwargs["name"]
    #         if "helpText" in kwargs:
    #             self.helpText = kwargs["helpText"]
    #         else:
    #             self.helpText = ""
    #         if "run_before" in kwargs:
    #             self.run_before = kwargs["run_before"]
    #         else:
    #             self.run_before = []
    #         if "run_after" in kwargs:
    #             self.run_after = kwargs["run_after"]
    #         else:
    #             self.run_after = []
    #         if "input" not in kwargs:
    #             self.input = []
    #         else:
    #             self.input = []
    #             for input in kwargs["input"]:
    #                 self.input.append(PluginCommandInput(structure=input))
    