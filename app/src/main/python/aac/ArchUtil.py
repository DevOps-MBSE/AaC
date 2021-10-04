import ArchParser
import os

primitives = []

def search(model, input_keys):
    """
    searches a dict for the contents given a set of keys
    """
    # print("searching for keys: {}",format(keys))
    keys = input_keys.copy()
    if len(keys) == 0:
        print("search error - empty keys")
        return []
    search_key = keys.pop(0)
    final_key = len(keys) == 0
    if not isinstance(model, dict):
        print("search error - model is not a dict")
        return []
    else:
        if search_key in model:
            model_value = model[search_key]
            if final_key:
                if isinstance(model_value, list):
                    return model_value
                else:
                    retVal = []
                    retVal.append(model_value)
                    return retVal

            if isinstance(model_value, dict):    
                return search(model[search_key], keys)
            elif isinstance(model_value, list):
                retVal = []
                for model_item in model_value:
                    # print(model_item)
                    if isinstance(model_item, dict):
                        retVal.extend(search(model_item, keys))
                    else:
                        print("serach error - lists can only contain dicts")
                return retVal
            else:
                print("search error - keys not found")
                return []
        else:
            # not an error, just zero search results
            return []

def getAaCSpec():
    """
    Gets the specification for Architecture-as-Code iteself.  The AaC model specification is defined as an AaC model and is needed for model validation. 
    """
    # get the AaC.yaml spec for architecture modeling
    file_path = str(os.path.realpath(__file__))

    this_file_path = os.path.dirname(os.path.realpath(__file__))
    relpath_to_aac_yaml = "../../../model/aac/AaC.yaml"
    aac_model_file = parse_path = os.path.join(this_file_path, relpath_to_aac_yaml) 
    
    model_types, data_types, enum_types, use_case_types = ArchParser.parse(aac_model_file)

    return model_types, data_types, enum_types

def getPrimitives():

    global primitives

    if len(primitives) == 0:
        
        model_types, data_types, enum_types = getAaCSpec()
        primitives = search(enum_types["Primitives"], ["enum", "values"])
    
    return primitives
