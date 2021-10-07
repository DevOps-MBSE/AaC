import argparse

from jellyfish import json, parser, puml

list_suffix = "[]"
enum_types = {}
data_types = {}
model_types = {}

if __name__ == "__main__":
    # print ("AaC is running")

    argParser = argparse.ArgumentParser()
    command_parser = argParser.add_subparsers(dest="command")
    validate_cmd = command_parser.add_parser(
        "validate", help="ensures the yaml is valid per teh AaC schema"
    )
    puml_component_cmd = command_parser.add_parser(
        "puml-component",
        help="generates plant UML component diagram from the YAML model",
    )
    puml_sequence_cmd = command_parser.add_parser(
        "puml-sequence",
        help="generates plant UML sequience diagram from the YAML use case",
    )
    puml_object_cmd = command_parser.add_parser(
        "puml-object", help="generates plant UML object diagram from the YAML model"
    )
    json_cmd = command_parser.add_parser("json", help="prints the json version of the yaml model")

    argParser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = argParser.parse_args()

    model_file = args.yaml
    # print(model_file)

    if args.command == "validate":
        try:
            parser.parse(model_file)
            print("Model [{}] is valid".format(model_file))
        except RuntimeError:
            print("Model [{}] is invalid".format(model_file))

    if args.command == "json":
        print(json.toJson(model_file))

    if args.command == "puml-component":
        print(puml.umlComponent(model_file))

    if args.command == "puml-sequence":
        print(puml.umlSequence(model_file))

    if args.command == "puml-object":
        print(puml.umlObject(model_file))
