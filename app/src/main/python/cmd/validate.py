import os
import json
import yaml
import jsonschema

def validate_arch(model_file: str):
    is_schema_valid, root = validate_against_schema(model_file)
    if (not is_schema_valid):
        return is_schema_valid, root

    type_name_list = ["string", "int", "number", "bool"]
    # validate uses statements
    if "uses" in root.keys():
        for use in root["uses"]:
            uses_path = use["path"]
            uses_name = use["name"]
            type_name_list.append(uses_name)
            f = open(model_file)
            base = os.path.dirname(f.name)
            check_me = base + "/" + uses_path

            # ensure uses path exists
            if (not os.path.exists(check_me)):
                return False, model_file + "- uses path does not exist [" + uses_path + "]"

            # ensure uses path is valid arch file
            is_valid, use_root = validate_arch(check_me)
            if (not is_valid):
                return False, use_root
            
            # if a data use ensure uses name is defined in data
            if ("data" in use_root.keys()):
                if (use_root["data"]["name"] != uses_name):
                    return False, "use path [" + uses_path + "] does not define [" + uses_name + "]"

            # if a model use ensure uses name is defined in the model
            if ("model" in use_root.keys()):
                if (use_root["model"]["name"] != uses_name):
                    return False, "use path [" + uses_path + "] does not define [" + uses_name + "]"

    # validate named types
    if "model" in root.keys():
        #includes (includes is optional in the schema)
        if ("includes" in root["model"].keys()):
            for incl in root["model"]["includes"]:
                if (not incl["type"] in type_name_list):
                    return False, "model [" + model_file + "] include contains unknown type [" + incl["type"] + "]"
        #inputs
        for input in root["model"]["inputs"]:
            if (not input["type"] in type_name_list):
                return False, "model [" + model_file + "] input contains unknown type [" + input["type"] + "]"
        #outputs
        for output in root["model"]["outputs"]:
            if (not output["type"] in type_name_list):
                return False, "model [" + model_file + "] output contains unknown type [" + output["type"] + "]"

    if "data" in root.keys():
        for field in root["data"]["fields"]:
            
            if (not field["type"] in type_name_list):
                return False, "data [" + model_file + "] field [" + field["name"] + "] contains unknown type [" + field["type"] + "]"

    return True, root

def validate_against_schema(model_file):
    root = ''
    with open(model_file, 'r') as file:
        contents = file.read()
        root = yaml.load(contents, Loader=yaml.FullLoader)

    schema_file = file_path = os.path.realpath(__file__).replace('cmd/validate.py', '/aac-schema.json')
    schema = ''
    with open(schema_file, 'r') as file:
        schema = json.load(file)

    # validate against schema
    try:
        jsonschema.validate(root, schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = model_file + " failed schema validation"
        return False, err

    return True, root