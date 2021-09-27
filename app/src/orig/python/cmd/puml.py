import os
from .validate import validate_against_schema

def print_plant_uml(yaml_file):
    
    print("@startuml")
    print_model_content(yaml_file, [])
    print("@enduml")
        
def print_model_content(yaml_file, existing):

    is_valid, root = validate_against_schema(yaml_file)
    if (not is_valid):
        raise os.error(root)

    model_name = root["model"]["name"]
    if ("model" in root.keys()):
        # first let's do this the unsophisticated way
        if ("inputs" in root["model"]):
            for input in root["model"]["inputs"]:
                if (not input["type"] in existing):
                    print("interface ", input["type"])
                    existing.append(input["type"])

        if ("outputs" in root["model"]):
            for output in root["model"]["outputs"]:
                if (not output["type"] in existing):
                    print("interface ", output["type"])
                    existing.append(output["type"])

        if ("includes" in root["model"]):
            print("package \"", model_name, "\" {")
            existing.append(model_name)
            for incl in root["model"]["includes"]:
                #get model path
                incl_type = incl["type"]
                use_path = get_use_path(incl_type, root)

                # ensure uses path exists
                f = open(yaml_file)
                base = os.path.dirname(f.name)
                check_me = base + "/" + use_path
                if (not os.path.exists(check_me)):
                    raise os.error(yaml_file + "- uses path does not exist [" + use_path + "]")

                print_model_content(check_me, existing)
            print("}")
        else:
            #inputs
            if ("inputs" in root["model"]):
                for input in root["model"]["inputs"]:
                    print(input["type"], " -> [", model_name, "] : ", input["name"])
            #outputs
            if ("outputs" in root["model"]):
                for output in root["model"]["outputs"]:
                    print("[", model_name, "] -> ", output["type"], " : ", output["name"])

def get_use_path(name, root):
    for use in root["uses"]:
        if (use["name"] == name):
            return use["path"]
    return None

   