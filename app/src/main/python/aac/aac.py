from abc import ABC, abstractmethod
import argparse
import os
import yaml
import json

known_types = ["string", "int", "number", "bool", "date", "file"]
list_suffix = "[]"
data_types = {}
model_types = {}

class Data:
    def __init__(self, **entries):
        self.__dict__.update(entries)


if __name__ == '__main__':
    print ("AaC is running")

    parser = argparse.ArgumentParser()
    command_parser = parser.add_subparsers(dest='command')
    validate_cmd = command_parser.add_parser('validate', help="ensures the yaml is valid per teh AaC schema")
    puml_cmd = command_parser.add_parser('puml', help="generates plant UML from the YAML model")
    json_cmd = command_parser.add_parser('json', help="prints the json version of the yaml model")
    
    parser.add_argument("yaml", type=str, help="the path to your architecture yaml")

    args = parser.parse_args()

    model_file = args.yaml

    roots = {}
    all_as_dict = {}
    with open(model_file, 'r') as file:
        contents = file.read()
        roots = yaml.load_all(contents, Loader=yaml.FullLoader)
        roots2 = yaml.load_all(contents, Loader=yaml.FullLoader)
        
        roots_count = 0
        for root in roots:
            all_as_dict.update(root)
            roots_count = roots_count + 1
        
        for root2 in roots2:
            all_as_dict.update(root2)

        print("roots_count: " + str(roots_count))
        print("all_as_dict size:" + str(len(all_as_dict.keys())))
        print("all_as_dict:" + json.dumps(all_as_dict))
        for root in roots:
            if "import" in root.keys():
                for imp in root["import"]:
                    print("found a import reference")
                    print(imp)
            if "data" in root.keys():
                for data in root["data"]:
                    print("found a data item:" + data["name"])
                    data_types[data["name"]] = data
            if "model" in root.keys():
                for model in root["model"]:
                    print("found a model item: " + model["name"])
                    model_types[model["name"]] = model
            

        print(json.dumps(data_types))
        print(json.dumps(model_types))