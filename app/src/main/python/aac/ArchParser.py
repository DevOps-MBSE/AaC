import os
import yaml

def parse(archFile: str):

    enum_types = {}
    data_types = {}
    model_types = {}

    arch_file_path = os.path.dirname(os.path.realpath(archFile))
    # print("parsing {} in directory {}".format(archFile, arch_file_path))

    with open(archFile, 'r') as file:
        contents = file.read()
        roots = yaml.load_all(contents, Loader=yaml.FullLoader)
        
        for root in roots:
            if "import" in root.keys():   # TODO this hasn't been tested
                for imp in root["import"]:
                    # parse the imported files
                    parse_path = ""
                    if imp.startswith("."):
                        # handle relative path
                        parse_path = os.path.join(arch_file_path, imp)
                    else:
                        parse_path = imp
                    imp_models, imp_data, imp_enum = parse(parse_path)

                    #add imports to the return dicts
                    enum_types = enum_types | imp_enum
                    data_types = data_types | imp_data
                    model_types = model_types | imp_models
                        
            if "enum" in root.keys():
                enum_types[root["enum"]["name"]] = root
            if "data" in root.keys():
                data_types[root["data"]["name"]] = root
            if "model" in root.keys():
                model_types[root["model"]["name"]] = root
   
    return model_types, data_types, enum_types