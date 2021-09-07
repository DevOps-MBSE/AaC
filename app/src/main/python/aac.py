import sys
import os
import json
import yaml
import argparse
import jsonschema

def validate_arch(model_file: str) -> bool:

    print("Processing Model: ", model_file)

    model = ''
    with open(model_file, 'r') as file:
        contents = file.read()
        model = yaml.load(contents, Loader=yaml.FullLoader)

    schema_file = file_path = os.path.realpath(__file__).replace('aac.py', 'data-schema.json')
    schema = ''
    with open(schema_file, 'r') as file:
        schema = json.load(file)

    jsonschema.validate(model, schema)
    return model

def print_json(model):
    print(model)




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(dest='command')
    validate_cmd = command_parser.add_parser('validate', help="ensures the yaml is valid per teh AaC schema")
    json_cmd = command_parser.add_parser('json', help="prints the json version of the yaml model")
    
    parser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = parser.parse_args()

    print("command = ", args.command)
    print("yaml = ", args.yaml)

    if (args.command == "validate"):
        yaml_file = args.yaml
        model = validate_arch(yaml_file)
        if (model == None):
            print(args.yaml, " is not valid.")
        else:
            print(args.yaml, " is valid.")
    
    elif (args.command == "json"):
        yaml_file = args.yaml
        model = validate_arch(yaml_file)
        print_json(model)

    else:
        parser.print_help()
    