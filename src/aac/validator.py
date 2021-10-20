"""Validate a model per the AaC DSL."""

# TODO: Replace "magic strings" with a more maintainable solution
# TODO: Generalize get_all_errors to handle all (or at least most of) the cases
# TODO: Switch from using isinstance(...) for type checking to something that can handle
#       AaC-defined types.

from enum import Enum
from typing import Union

from iteration_utilities import flatten

from aac import util


def is_valid(model: dict) -> bool:
    """Check if MODEL is valid per the AaC DSL.

    Return True if MODEL is valid; False, otherwise.
    """
    return len(get_all_errors(model)) == 0


def get_all_errors(model: dict) -> list:
    """Return all validation errors for MODEL.

    Return a list of all the validation errors found for MODEL. If the MODEL is
    valid, return an empty list.
    """

    def collect_errors(model):
        x = dict(list(model.values())[0])
        kind = x["name"] if "name" in x else ""
        return (
            get_all_parsing_errors(model)
            + get_all_cross_reference_errors(kind, model)
            + get_all_enum_errors(model)
            + get_all_data_errors(model)
            + get_all_usecase_errors(model)
            + get_all_model_errors(model)
            + get_all_extension_errors(model)
        )

    return list(flatten(map(collect_errors, model.values())))


def get_all_parsing_errors(model: dict) -> list:
    """Return all parsing errors."""

    def get_unrecognized_root_errors(root):
        if root not in util.get_roots():
            return "{} is not a recognized AaC root type".format(root)

    return filter_none_values(map(get_unrecognized_root_errors, model.keys()))


def get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL.

    Return a list of all the validation errors found for the enumeration MODEL.
    If the enumeration MODEL is valid, return an empty list.
    """

    def is_enum_model(model):
        return kind in model

    kind = "enum"
    if is_enum_model(model):
        return get_all_errors_for(model, kind=kind, items=load_aac_fields_for(kind))

    return []


def get_all_errors_for(model: dict, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    model = model[properties["kind"]] if "kind" in properties else model
    items = properties["items"]

    props = [i["name"] for i in items]
    types = [i["type"] for i in items]
    required = [i["name"] for i in items if i["required"]]

    return filter_none_values(
        get_all_errors_if_missing_required_properties(model, required),
        get_all_errors_if_unrecognized_properties(model, props),
    )


def filter_none_values(*xs: list) -> list:
    """Return XS without None values."""
    return list(filter(lambda x: x, flatten(xs)))


def get_all_errors_if_missing_required_properties(model: dict, required: list) -> iter:
    """Get error messages if the model is missing required properties.

    Return an iterable object containing any error messages for all REQUIRED
    properties that are not present in the MODEL. If the MODEL has all of the
    required properties, the returned collection will be empty.
    """

    def get_error_if_missing_required_property(key):
        if key not in model.keys():
            return f"missing required field '{key}' in model '{model}'"

    return map(get_error_if_missing_required_property, required)


# TODO: Refactor
def get_all_cross_reference_errors(kind: str, model: dict) -> iter:
    """Validate all cross references.

    Returns:
      Returns an iterable object that contains all error messages related to
      unrecognized cross-references in a model.
    """
    data, enums = util.get_aac_spec()
    models = {kind: model} | data | enums
    valid_types = list(models.keys()) + util.get_primitives()

    def is_valid_type(type):
        return type.strip("[]") not in valid_types

    def validate_data_references(data):
        errors = []
        for name, spec in data.items():
            for spec_type in util.search(spec, ["data", "fields", "type"]):
                if is_valid_type(spec_type):
                    errors.append(f"unrecognized type {spec_type} used in {name}")
        return errors

    def validate_model_references(models):
        errors = []
        for name, spec in models.items():
            spec_types = util.search(spec, ["model", "components", "type"])
            spec_types.extend(util.search(spec, ["model", "behavior", "input", "type"]))
            spec_types.extend(util.search(spec, ["model", "behavior", "output", "type"]))
            for spec_type in spec_types:
                if is_valid_type(spec_type):
                    errors.append(f"unrecognized type {spec_type} used in {name}")
        return errors

    def validate_enum_references(models, data, enums):
        enum_paths = {}
        for enum_name in enums:
            if enum_name == "Primitives":
                continue
            found_paths = _find_enum_field_paths(enum_name, "model", "model", data, enums)
            enum_paths[enum_name] = found_paths

        # then ensure the value provided in the model is defined in the enum
        errors = []

        valid_values = []
        for enum_name in enum_paths:
            if enum_name == "Primitives":
                continue

            valid_values = util.search(enums[enum_name], ["enum", "values"])

            for model_name in models:
                for path in found_paths:
                    for result in util.search(models[model_name], path):
                        if result not in valid_values:
                            errors.append(
                                f"Model {model_name} entry {path} has a value {result} not allowed in the enumeration {enum_name}: {valid_values}"
                            )
        return errors

    def _find_enum_field_paths(find_enum, data_name, data_type, data, enums) -> list:
        data_model = data[data_type]
        fields = util.search(data_model, ["data", "fields"])
        enum_fields = []
        for field in fields:
            field_type = field["type"].strip("[]")
            if field_type in enums.keys():
                if field_type == find_enum:
                    enum_fields.append([field["name"]])
            elif field_type not in util.get_primitives():
                found_paths = _find_enum_field_paths(
                    find_enum, field["name"], field_type, data, enums
                )
                for found in found_paths:
                    entry = found.copy()
                    enum_fields.append(entry)

        ret_val = []
        for enum_entry in enum_fields:
            entry = enum_entry.copy()
            entry.insert(0, data_name)
            ret_val.append(entry)
        return ret_val

    data = util.get_models_by_type(models, "data")
    enums = util.get_models_by_type(models, "enum")
    models = util.get_models_by_type(models, "model")
    return filter_none_values(
        validate_data_references(data),
        validate_model_references(models),
        validate_enum_references(models, data, enums),
    )


def get_all_errors_if_unrecognized_properties(model: dict, props: list) -> iter:
    """Get error messages if the model has unrecognized properties.

    Return an iterable object containing any error messages for all properties
    found in the MODEL that are not recognized as valid for the specified model.
    If the MODEL's has no unrecognized properties, the returned collection will
    be empty.
    """

    def get_error_if_property_is_unrecognized(key):
        if key not in props:
            return f"unrecognized field named '{key}' found in model '{model}'"

    return map(get_error_if_property_is_unrecognized, model.keys())


def get_all_data_errors(model: dict) -> list:
    """Return all validation errors for the data MODEL.

    Return a list of all the validation errors found for the data MODEL. If the
    data MODEL is valid, return an empty list.
    """

    def is_data_model(model):
        return kind in model

    kind = "data"
    if is_data_model(model):
        data = model[kind]
        return filter_none_values(
            get_all_errors_for(model, kind=kind, items=load_aac_fields_for(kind)),
            get_all_non_root_element_errors(data, "fields", list, load_aac_fields_for("Field")),
            get_all_required_field_errors(data),
        )

    return []


# TODO: items is a horrible name, here, find a better one
def get_all_non_root_element_errors(
    model: Union[dict, list], element: str, type: type, items: list
) -> list:
    """Return all validation errors for the non-root element MODELs.

    Return a list of all the validation errors found for non-root element
    MODELs. If the non-root element MODELs are valid, return an empty list.
    """

    def has_element(model):
        return element in model and isinstance(model[element], type)

    def get_field_errors(model):
        if has_element(model):
            model = [model[element]] if isinstance(model[element], dict) else model[element]
            return flatten(map(lambda x: get_all_errors_for(x, items=items), model))
        return []

    model = model if isinstance(model, list) else [model]
    return flatten(map(get_field_errors, model))


def get_all_required_field_errors(model: dict) -> list:
    """Return all validation errors for the required fields of the MODEL.

    Return a list of all the validation errors found for the required fields of
    the MODEL. If the required field of the MODEL is valid, return an empty
    list.
    """

    def has_required_fields(model: dict):
        return "required" in model and isinstance(model["required"], list)

    def get_required_field_error(required):
        if required not in map(lambda f: f["name"], model["fields"]):
            return "reference to undefined required field: {}".format(required)

    if has_required_fields(model):
        return filter_none_values(map(get_required_field_error, model["required"]))

    return []


def get_all_usecase_errors(model: dict) -> list:
    """Return all validation errors for the usecase MODEL.

    Return a list of all the validation errors found for the usecase MODEL. If
    the usecase MODEL is valid, return an empty list.
    """

    def is_usecase(model):
        return "usecase" in model

    if is_usecase(model):
        usecase = model["usecase"]
        return filter_none_values(
            get_all_errors_for(model, kind="usecase", items=load_aac_fields_for("usecase")),
            get_all_non_root_element_errors(
                usecase, "participants", list, load_aac_fields_for("Field")
            ),
            get_all_non_root_element_errors(usecase, "steps", list, load_aac_fields_for("Step")),
        )

    return []


def get_all_model_errors(model: dict) -> list:
    """Return all validation errors for the system MODEL.

    Return a list of all the validation errors found for the system MODEL. If
    the system MODEL is valid, return an empty list.
    """

    def is_model(model):
        return "model" in model

    def has_behaviors(model):
        return "behavior" in model and isinstance(model["behavior"], list)

    if is_model(model):
        m = model["model"]
        behaviors = m["behavior"] if has_behaviors(m) else []
        return filter_none_values(
            get_all_errors_for(model, kind="model", items=load_aac_fields_for("model")),
            get_all_non_root_element_errors(m, "behavior", list, load_aac_fields_for("Behavior")),
            get_all_non_root_element_errors(m, "components", list, load_aac_fields_for("Field")),
            get_all_non_root_element_errors(
                behaviors, "acceptance", list, load_aac_fields_for("Scenario")
            ),
            get_all_non_root_element_errors(
                behaviors, "input", list, load_aac_fields_for("Field")
            ),
            get_all_non_root_element_errors(
                behaviors, "output", list, load_aac_fields_for("Field")
            ),
        )

    return []


def get_all_extension_errors(model: dict) -> list:
    """Return all validation errors for the system MODEL.

    Return a list of all the validation errors found for the system MODEL. If
    the system MODEL is valid, return an empty list.
    """

    def is_ext(model):
        return "ext" in model

    def is_data_ext(model):
        return "dataExt" in model and isinstance(model["dataExt"], dict)

    def is_enum_ext(model):
        return "enumExt" in model and isinstance(model["enumExt"], dict)

    def get_all_errors_if_data_and_enum_extension_combined(model):
        if is_data_ext(model) and is_enum_ext(model):
            return ["cannot combine enumExt and dataExt in the same extension"]
        return []

    if is_ext(model):
        ext = model["ext"]
        kind, type, items = (
            ("dataExt", dict, load_aac_fields_for("DataExtension"))
            if is_data_ext(ext)
            else ("enumExt", dict, load_aac_fields_for("EnumExtension"))
        )
        return filter_none_values(
            get_all_errors_for(model, kind="ext", items=load_aac_fields_for("extension")),
            get_all_errors_if_data_and_enum_extension_combined(ext),
            get_all_non_root_element_errors(ext, kind, type, items),
            # TODO: Not generic enough
            get_all_non_root_element_errors(ext[kind], "add", list, load_aac_fields_for("Field"))
            if is_data_ext(ext)
            else [],
        )

    return []


def load_aac_fields_for(kind: str) -> list:
    """Get the AaC fields and their properties for the specified KIND of item."""
    data, _ = util.get_aac_spec()
    values = data[kind]["data"]
    fields = values["fields"]

    def is_required_field(field):
        return "required" in values and field["name"] in values["required"]

    def add_required_value_to_field(field):
        return field | {"required": is_required_field(field)}

    return list(map(add_required_value_to_field, fields))
