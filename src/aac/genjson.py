import json


def toJson(parsed_models) -> str:
    just_dicts = []
    for name in parsed_models:
        just_dicts.append(parsed_models[name])
    print(json.dumps(just_dicts))
    return 
