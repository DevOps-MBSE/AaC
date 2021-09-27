from .validate import validate_against_schema

def print_json(yaml_file):
    is_valid, model = validate_against_schema(yaml_file)
    print(model)