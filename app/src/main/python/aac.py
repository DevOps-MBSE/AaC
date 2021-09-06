import sys
import os
import json
import yaml
from jsonschema import validate


def validateArch(model_file: str) -> bool:

    print("Processing Model: ", model_file)

    model = ''
    with open(model_file, 'r') as file:
        contents = file.read()
        model = yaml.load(contents, Loader=yaml.FullLoader)

    schema_file = file_path = os.path.realpath(__file__).replace('aac.py', 'data-schema.json')
    schema = ''
    with open(schema_file, 'r') as file:
        schema = json.load(file)

    validate(model, schema)
    return model

def process(model):
    print(model)




if __name__ == '__main__':
    model = validateArch(sys.argv[1])
    
    process(model)
    