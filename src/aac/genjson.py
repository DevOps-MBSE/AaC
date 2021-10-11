import json
import aac
from aac.AacCommand import AacCommand


@aac.hookimpl
def get_commands():
    my_cmd = AacCommand("json", "Converts an AaC model to JSON", toJson)
    return [my_cmd]


@aac.hookimpl
def get_base_model_extensions():
    return None


def toJson(arch_file, parsed_models) -> str:
    just_dicts = []
    for name in parsed_models:
        just_dicts.append(parsed_models[name])
    print(json.dumps(just_dicts))
    return
