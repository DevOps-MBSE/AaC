import argparse

from cmd.puml import print_plant_uml
from cmd.json import print_json
from cmd.validate import validate_arch


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
        print_json(yaml_file)

    elif (args.command == "puml"):
        yaml_file = args.yaml
        print_plant_uml(yaml_file)

    else:
        parser.print_help()
    