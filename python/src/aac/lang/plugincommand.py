from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators, Factory
import attr
from aac.execute.aac_execution_result import LanguageError
from aac.lang.plugincommandinput import PluginCommandInput

@dataclass(frozen=True)
class PluginCommand():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    helpText: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    run_before: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    run_after: list[str] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    input: list[PluginCommandInput] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        helpText = None
        if "helpText" in data:
            helpText = data.pop("helpText")
        run_before = data.pop("run_before", [])
        run_after = data.pop("run_after", [])
        input_data = data.pop("input", [])
        input = [PluginCommandInput.from_dict(input_data) for input_data in input_data]
        return cls(helpText=helpText, run_before=run_before, run_after=run_after, input=input, **data)
