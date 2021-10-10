import argparse

from aac import genjson, parser, puml, echo

list_suffix = "[]"
enum_types = {}
data_types = {}
model_types = {}


def runCLI():
    # print ("AaC is running")

    argParser = argparse.ArgumentParser()
    command_parser = argParser.add_subparsers(dest="command")
    # validate_cmd =
    command_parser.add_parser(
        "validate", help="ensures the yaml is valid per teh AaC schema"
    )
    # puml_component_cmd =
    command_parser.add_parser(
        "puml-component",
        help="generates plant UML component diagram from the YAML model",
    )
    # puml_sequence_cmd =
    command_parser.add_parser(
        "puml-sequence",
        help="generates plant UML sequience diagram from the YAML use case",
    )
    # puml_object_cmd =
    command_parser.add_parser(
        "puml-object", help="generates plant UML object diagram from the YAML model"
    )
    # echo_plugin_cmd =
    command_parser.add_parser("echo", help="Runs the echo plugin example")

    # json_cmd =
    command_parser.add_parser("json", help="prints the json version of the yaml model")

    argParser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = argParser.parse_args()

    model_file = args.yaml
    # print(model_file)

    parsed_models = {}
    try:
        parsed_models = parser.parse(model_file)
    except RuntimeError:
        print(f"Model [{model_file}] is invalid")

    if args.command == "validate":
        print(f"Model [{model_file}] is valid")

    if args.command == "json":
        genjson.toJson(parsed_models)

    if args.command == "puml-component":
        puml.umlComponent(parsed_models)

    if args.command == "puml-sequence":
        puml.umlSequence(parsed_models)

    if args.command == "puml-object":
        puml.umlObject(parsed_models)

    if args.command == "echo":
        echo.demonstrate_echo("Hello World!")
