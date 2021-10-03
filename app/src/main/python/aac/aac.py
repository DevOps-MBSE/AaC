import argparse
import ArchValidator
import ArchJson
import ArchPuml
import yaml

list_suffix = "[]"
enum_types = {}
data_types = {}
model_types = {}

if __name__ == '__main__':
    # print ("AaC is running")

    argParser = argparse.ArgumentParser()
    command_parser = argParser.add_subparsers(dest='command')
    validate_cmd = command_parser.add_parser('validate', help="ensures the yaml is valid per teh AaC schema")
    puml_cmd = command_parser.add_parser('puml', help="generates plant UML from the YAML model")
    json_cmd = command_parser.add_parser('json', help="prints the json version of the yaml model")
    
    argParser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = argParser.parse_args()

    model_file = args.yaml
    # print(model_file)

    if (args.command == "validate"):
        validation_result = ArchValidator.validate(model_file)
        print(yaml.dump(validation_result))
    
    if (args.command == "json"):
        print(ArchJson.toJson(model_file))

    if (args.command == "puml"):
        print(ArchPuml.toPuml(model_file))