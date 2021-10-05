class Data:
    spec = {"data": 
        [{"name" : "string"},
        {"fields" : "Field[]"},
        {"required" : "string[]"}],
        "Field":
        [{"name" : "string"},
        {"type" : "string"},
        {"required" : "string[]"}]}

    def __init__(self, data_type_name, data):
        '''
        @param name - name of the item
        @param data_type_name - type of the item from the spec
        @param data - the data to load into the class
        '''
        # keys = data.keys()
        # if len(keys) > 1:
        #     raise RuntimeError("data must be len 1")

        if not data_type_name in Data.spec:
            raise RuntimeError("unknown data type {}".format(data_type_name))

        data_spec = Data.spec[data_type_name]
        for spec_field in data_spec:
            for spec_field_name in spec_field:
                if "required" == spec_field_name:
                    # required is only used for validation and won't be present in the actual data
                    continue
                spec_field_type = spec_field[spec_field_name]
                isList = spec_field_type.endswith("[]")
                field_type = ""
                if isList:
                    field_type = spec_field_type[0:-2]
                else:
                    field_type = spec_field_type

                field_value = ""
                # if primitive
                if field_type in ["string"]:
                    # this should work for single values and lists
                    field_value = data[spec_field_name]
                
                # else complex type
                else:
                    # if list of complex types  
                    if isList:
                        field_value = []
                        for entry in data[spec_field_name]:
                            field_value.append(Data(field_type, entry))

                    # else single complex type
                    else:
                        field_value = Data(field_type, data[spec_field_name])

                # add the field name and value
                self.__dict__[spec_field_name] = field_value

    def __getattr__(self, key):
        print("Data get: {}".format(key))
        return self.__dict__[key]

    def __setattr__(self, key, value):
        print("Data set: {}, {}".format(key, value))
        self.__dict__[key] = value

# my_dict = [{"name" : "import", "import" : ["imp1", "imp2", "imp3"]}, 
#             {"name" : "enum", "values" : {"name" : "primitives", "values" : ["int", "number", "string", "date"]}},
#             {"name" : "data", "fields" : [{"name" : "val1", "type" : "string"}, {{"name" : "val2", "type" : "string"}}], "required" : ["val1"]}]

spec = {"data": 
        [{"name" : "string"},
        {"fields" : "Field[]"},
        {"required" : "string[]"}],
        "Field":
        [{"name" : "string"},
        {"type" : "string"},
        {"required" : "string[]"}]}

data = {"data" : 
        {"name": "model",
        "fields": [
            {"name": "name",
            "type": "string"},
            {"name": "description",
            "type": "string"},
            {"name": "components",
            "type": "Field[]"}],
        "required": ["name"] }}

d = Data("data", data["data"])

print(d.name)
for item in d.fields:
    print(item.name)
    print(item.type)
