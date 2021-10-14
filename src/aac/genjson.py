import json
import aac
from aac.AacCommand import AacCommand


@aac.hookimpl
def get_commands() -> list[AacCommand]:
    """
    Provides the json command for integration into the CLI.
    """
    my_cmd = AacCommand("json", "Converts an AaC model to JSON", toJson)
    return [my_cmd]


@aac.hookimpl
def get_base_model_extensions() -> str:
    """
    This plugin doesn't define any extensions, so returns None.
    """
    return None


def toJson(_, parsed_models: dict[str, dict]):
    """
    Prints the parsed_models parameter values in JSON format.
    """
    just_dicts = []
    for name in parsed_models:
        just_dicts.append(parsed_models[name])
    print(json.dumps(just_dicts))
    return
