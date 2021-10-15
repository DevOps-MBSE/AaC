"""
The AaC validation module.  Validates a model against the model spec.
"""
from aac import util


def validate(validate_me: dict[str, dict]) -> tuple[bool, list[str]]:
    """
    Performs validation against the validate_me arg using the AaC model spec.
    """

    found_invalid = False
    err_msg_list = []

    for model in validate_me.values():
        is_valid, err_msg = _validate_general(model)
        if not is_valid:
            # print("Enum Validation Failed: {}".format(errMsg))
            found_invalid = True
            err_msg_list = err_msg_list + err_msg

    # combine parsed types and AaC built-in types
    aac_data, aac_enums = util.get_aac_spec()
    all_types = validate_me | aac_data | aac_enums
    is_valid, err_msg = _validate_cross_references(all_types)
    if not is_valid:
        found_invalid = True
        err_msg_list = err_msg_list + err_msg

    is_valid, err_msg = _validate_enum_values(validate_me)
    if not is_valid:
        found_invalid = True
        err_msg_list = err_msg_list + err_msg

    for ext in util.get_models_by_type(validate_me, "ext"):
        type_to_extend = validate_me[ext]["ext"]["type"]
        if type_to_extend in aac_data or type_to_extend in aac_enums:
            apply_extension(validate_me[ext], aac_data, aac_enums)
        else:
            apply_extension(validate_me[ext],
                            util.get_models_by_type(validate_me, "data"),
                            util.get_models_by_type(validate_me, "enum"))

    return not found_invalid, err_msg_list


def _validate_general(validate_me: dict) -> tuple[bool, list]:
    """
    Validate any given AaC model from the root.
    """

    model = validate_me.copy()
    # remove any imports before validation
    if "import" in model:
        del model["import"]

    # any model can only have a single root
    if len(list(model.keys())) > 1:
        return False, ["AaC Validation Error: yaml file has more than one root defined"]

    # ensure the model has a known root
    root_name = list(model.keys())[0]
    if root_name not in util.get_roots():
        return False, [f"AaC Validation Error: yaml file has an unrecognized root [{root_name}].  Known roots {util.get_roots()}"]

    # get the root type to validate against
    root_type = ""
    aac_data, aac_enums = util.get_aac_spec()
    for field in util.search(aac_data["root"], ["data", "fields"]):
        if field["name"] == root_name:
            root_type = field["type"]
            break

    return _validate_model_entry(root_name, root_type, model[root_name], aac_data, aac_enums)


def _validate_cross_references(all_models: dict[str, dict]):
    """
    Process all provided models and ensure known type references are defined in the model.
    """
    all_types = list(all_models.keys())
    all_types.extend(util.get_primitives())

    models = util.get_models_by_type(all_models, "model")
    data = util.get_models_by_type(all_models, "data")

    found_invalid = False
    err_msgs = []

    for model_name, data_entry in data.items():
        data_model_types = util.search(data_entry, ["data", "fields", "type"])
        # print("processing {} - data_model_types: {}".format(model_name, data_model_types))
        for data_model_type in data_model_types:
            _, base_type_name = _get_simple_base_type_name(data_model_type)
            if base_type_name not in all_types:
                found_invalid = True
                err_msgs.append(
                    "Data model [{}] uses undefined data type [{}]".format(
                        model_name, base_type_name
                    )
                )

    for model_name, model_entry in models.items():
        model_entry_types = util.search(model_entry, ["model", "components", "type"])
        model_entry_types.extend(util.search(model_entry, ["model", "behavior", "input", "type"]))
        model_entry_types.extend(util.search(model_entry, ["model", "behavior", "output", "type"]))
        # print("processing {} - model_entry_types: {}".format(model_name, model_entry_types))
        for model_entry_type in model_entry_types:
            _, base_type_name = _get_simple_base_type_name(model_entry_type)
            if base_type_name not in all_types:
                found_invalid = True
                err_msgs.append(f"Model model [{model_name}] uses undefined data type [{base_type_name}]")

    if not found_invalid:
        return True, ""
    else:
        return False, err_msgs


def _validate_enum_values(all_models: dict[str, dict]):
    """
    Checks to see that any value for an enum type is defined in the enum spec.
    """

    models = util.get_models_by_type(all_models, "model")
    data = util.get_models_by_type(all_models, "data")
    enums = util.get_models_by_type(all_models, "enum")

    # find serach paths to the usage
    enum_validation_paths = {}
    for enum_name in enums:
        if enum_name == "Primitives":
            # skip primitives
            continue
        found_paths = _find_enum_field_paths(enum_name, "model", "model", data, enums)
        # print("{} found_paths: {}".format(enum_name, found_paths))
        enum_validation_paths[enum_name] = found_paths

    # then ensure the value provided in the model is defined in the enum
    found_invalid = False
    err_msg_list = []

    valid_values = []
    for enum_name in enum_validation_paths:
        if enum_name == "Primitives":
            # skip primitives
            continue

        valid_values = util.search(enums[enum_name], ["enum", "values"])
        # print("Enum {} valid values: {}".format(enum_name, valid_values))

        for model_name in models:
            for path in found_paths:
                for result in util.search(models[model_name], path):
                    # print("Model {} entry {} has a value {} being validated by the enumeration {}: {}".format(model_name, path, result, enum_name, valid_values))
                    if result not in valid_values:
                        found_invalid = True
                        err_msg_list.append(f"Model {model_name} entry {path} has a value {result} not allowed in the enumeration {enum_name}: {valid_values}")

    if not found_invalid:
        return True, []

    return False, err_msg_list


def _find_enum_field_paths(find_enum, data_name, data_type, data, enums) -> list:
    # print("findEnumFieldPaths: {}, {}, {}".format(find_enum, data_name, data_type))
    data_model = data[data_type]
    fields = util.search(data_model, ["data", "fields"])
    enum_fields = []
    for field in fields:
        _, field_type = _get_simple_base_type_name(field["type"])
        if field_type in enums.keys():
            # only report the enum being serached for
            if field_type == find_enum:
                enum_fields.append([field["name"]])
            else:
                continue
        elif field_type not in util.get_primitives():
            found_paths = _find_enum_field_paths(find_enum, field["name"], field_type, data, enums)
            for found in found_paths:
                entry = found.copy()
                # entry.insert(0, field["name"])
                enum_fields.append(entry)

    ret_val = []
    for enum_entry in enum_fields:
        entry = enum_entry.copy()
        entry.insert(0, data_name)
        ret_val.append(entry)
    return ret_val


def _get_spec_required_fields(spec_model, name):
    return util.search(spec_model, [name, "data", "required"])


def _get_spec_field_names(spec_model, name):
    ret_val = []
    fields = util.search(spec_model, [name, "data", "fields"])
    for field in fields:
        ret_val.append(field["name"])
    return ret_val


def _get_simple_base_type_name(type_declaration):
    if type_declaration.endswith("[]"):
        return True, type_declaration[0:-2]

    return False, type_declaration


def _get_model_object_fields(spec_model, enum_spec, name):
    retVal = {}
    fields = util.search(spec_model, [name, "data", "fields"])
    for field in fields:
        isList, field_type_name = _get_simple_base_type_name(field["type"])
        isEnum = field_type_name in enum_spec.keys()
        isPrimitive = field_type_name in util.get_primitives()
        if not isEnum and not isPrimitive:
            retVal[field["name"]] = field["type"]

    return retVal


def _validate_model_entry(name: str, model_type: str, model: dict, data_spec: dict[str, dict], enum_spec: dict[str, dict]):
    """
    Validate an Architecture-as-Code model.  A model item is a root of the AaC approach.
    Unlike enum and data, the content and structure of a model is not "hard coded", but specified in the data definition of a model in the yaml file that models AaC itself.
    This was put in place to support extensibility and customization, but does create a bit of "inception" that can be difficult to reason about.

    :param model: The model to be validated.
    :param data_specs: The data definitions of the modelled system (including AaC base types).
    """

    # make sure the model fields are correct per the spec
    model_spec_fields = _get_spec_field_names(data_spec, model_type)
    model_spec_required_fields = _get_spec_required_fields(data_spec, model_type)
    model_fields = list(model.keys())

    # check that required fields are present
    is_valid, err_msg_list = _check_required_fields(name, model_fields, model_spec_required_fields)
    if not is_valid:
        return is_valid, err_msg_list

    # check that model fields are recognized per the spec
    is_valid, err_msg_list = _check_fields_known(name, model_fields, model_spec_fields)
    if not is_valid:
        return is_valid, err_msg_list

    # look for any field that is not a primitive type and validate the contents
    object_fields = _get_model_object_fields(data_spec, enum_spec, model_type)
    if len(object_fields) == 0:
        # there are only primitives, validation successful
        return True, []

    for field_name in object_fields:
        if field_name not in model.keys():
            # print("in model {} object field {} is not present but optional".format(name, field_name))
            continue
        field_type = object_fields[field_name]
        sub_model = model[field_name]
        isList, field_type_name = _get_simple_base_type_name(field_type)
        if isList:
            if not sub_model:  # list is empty
                pass
            else:
                for sub_model_item in sub_model:
                    isValid, errMsg = _validate_model_entry(
                        field_name, field_type_name, sub_model_item, data_spec, enum_spec
                    )
                    if not isValid:
                        return isValid, errMsg
        else:
            isValid, errMsg = _validate_model_entry(
                field_name, field_type_name, sub_model, data_spec, enum_spec
            )
            if not isValid:
                return isValid, errMsg

    return True, []


def _check_required_fields(name: str, model_fields: list[str], model_spec_required_fields: list[str]) -> tuple[bool, list[str]]:
    for required_field in model_spec_required_fields:
        if required_field not in model_fields:
            return False, [f"model {name} is missing required field {required_field}"]
    return True, []


def _check_fields_known(name: str, model_fields: list[str], model_spec_fields: list[str]) -> tuple[bool, list[str]]:
    for model_field in model_fields:
        if model_field not in model_spec_fields:
            return False, [f"model {name} contains unrecognized field {model_field}"]
    return True, []


def apply_extension(extension: dict, data: dict[str, dict], enums: dict[str, dict]):
    """
    Uses the provided extension to update data and enum definitions in the provided
    specification sets.
    """
    type_to_extend = extension["ext"]["type"]
    if "enumExt" in extension["ext"]:
        # apply the enum extension
        updated_values = (
            enums[type_to_extend]["enum"]["values"] + extension["ext"]["enumExt"]["add"]
        )
        enums[type_to_extend]["enum"]["values"] = updated_values
    else:
        # apply the data extension
        updated_fields = (
            data[type_to_extend]["data"]["fields"] + extension["ext"]["dataExt"]["add"]
        )
        data[type_to_extend]["data"]["fields"] = updated_fields

        if "required" in extension["ext"]["dataExt"]:
            updated_required = (
                data[type_to_extend]["data"]["required"] + extension["ext"]["dataExt"]["required"]
            )
            data[type_to_extend]["data"]["fields"] = updated_required
