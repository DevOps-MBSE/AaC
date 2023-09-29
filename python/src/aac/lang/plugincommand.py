from dataclasses import dataclass
from typing import Optional
from attr import attrib, validators, Factory
import attr
from aac.execute.aac_execution_result import LanguageError
from aac.lang.plugincommandinput import PluginCommandInput
from aac.lang.plugincommandreference import PluginCommandReference

@dataclass(frozen=True)
class PluginCommand():
    
    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    help_text: Optional[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(str)))
    run_before: list[PluginCommandReference] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    run_after: list[PluginCommandReference] = attrib(init=attr.ib(), validator=validators.instance_of(list))
    input: list[PluginCommandInput] = attrib(init=attr.ib(), validator=validators.instance_of(list))

    @classmethod
    def from_dict(cls, data):
        help_text = None
        if "help_text" in data:
            help_text = data.pop("help_text")
        run_before_data = data.pop("run_before", [])
        run_before = [PluginCommandReference.from_dict(rb_data) for rb_data in run_before_data] 
        run_after_data = data.pop("run_after", [])
        run_after = [PluginCommandReference.from_dict(ra_data) for ra_data in run_after_data] 
        input_data = data.pop("input", [])
        input = [PluginCommandInput.from_dict(input_data) for input_data in input_data]
        return cls(help_text=help_text, run_before=run_before, run_after=run_after, input=input, **data)
