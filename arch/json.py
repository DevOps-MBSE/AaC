import json

from arch import parser


def toJson(archFile) -> str:
    model_types, data_types, enum_types, use_case_types, ext_types = parser.parse(archFile)
    complete_dict = model_types | data_types | enum_types | use_case_types
    return_dicts = []
    for name in complete_dict:
        return_dicts.append(complete_dict[name])
    return json.dumps(return_dicts)
