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