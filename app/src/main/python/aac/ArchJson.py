import ArchParser
import ArchValidator
import json

def toJson(archFile) -> str:

    validation = ArchValidator.validate(archFile)
    if validation["result"]["isValid"]:
        model_types, data_types, enum_types = ArchParser.parse(archFile)
        complete_dict = model_types | data_types | enum_types
        return_dicts = []
        for name in complete_dict:
            return_dicts.append(complete_dict[name])
        return json.dumps(return_dicts)
    else:
        raise RuntimeError("Failed to validate {}".format(archFile), validation)
    