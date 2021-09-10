import sys
import os
import json
import yaml
import argparse
import jsonschema

def validate_arch(model_file: str) -> bool:
    model = ''
    with open(model_file, 'r') as file:
        contents = file.read()
        model = yaml.load(contents, Loader=yaml.FullLoader)

    schema_file = file_path = os.path.realpath(__file__).replace('aac.py', 'aac-schema.json')
    schema = ''
    with open(schema_file, 'r') as file:
        schema = json.load(file)

    # validate against schema
    try:
        jsonschema.validate(model, schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = model_file + " failed schema validation"
        return False, err

    type_name_list = ["string", "int", "number", "bool"]
    # validate uses statements
    if "uses" in model.keys():
        for use in model["uses"]:
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
            is_valid, msg = validate_arch(check_me)
            if (not is_valid):
                return False, msg
            else: 
                # ensure uses name is defined in path
                if (msg["data"]["name"] != uses_name):
                    return False, "use path [" + uses_path + "] does not define [" + uses_name + "]"

    # validate named types
    if "model" in model.keys():
        for action in model["model"]["actions"]:
            #inputs
            for input in action["inputs"]:
                if (not input["type"] in type_name_list):
                    return False, "model [" + model_file + "] action input contains unknown type [" + input["type"] + "]"
            #outputs
            for output in action["outputs"]:
                if (not output["type"] in type_name_list):
                    return False, "model [" + model_file + "] action output contains unknown type [" + output["type"] + "]"
    if "data" in model.keys():
        for field in model["data"]["fields"]:
            
            if (not field["type"] in type_name_list):
                return False, "data [" + model_file + "] field [" + field["name"] + "] contains unknown type [" + field["type"] + "]"

    return True, model

def print_json(model):
    print(model)

def print_plant_uml(model):
    model_name = model["model"]["name"]
    print("@startuml")
    
    # first let's do this the unsophisticated way
    
    #loop through actions
    for action in model["model"]["actions"]:
        action_name = action["name"]
        #inputs
        for input in action["inputs"]:
            print(input["name"], " -> [", model_name, "] : ", input["type"])
        #outputs
        for output in action["outputs"]:
            print("[", model_name, "] -> ", output["name"], " : ", output["type"])

    print("@enduml")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(dest='command')
    validate_cmd = command_parser.add_parser('validate', help="ensures the yaml is valid per teh AaC schema")
    puml_cmd = command_parser.add_parser('puml', help="generates plant UML from the YAML model")
    json_cmd = command_parser.add_parser('json', help="prints the json version of the yaml model")
    
    parser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = parser.parse_args()

    if (args.command == "validate"):
        yaml_file = args.yaml
        is_valid, model = validate_arch(yaml_file)
        if (not is_valid):
            print(args.yaml, " is not valid.")
            print("Issue: ", model)
        else:
            print(args.yaml, " is valid.")
    
    elif (args.command == "json"):
        yaml_file = args.yaml
        is_valid, model = validate_arch(yaml_file)
        print_json(model)

    elif (args.command == "puml"):
        yaml_file = args.yaml
        is_valid, model = validate_arch(yaml_file)
        print_plant_uml(model)

    else:
        parser.print_help()
    