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

    def collect_errors(m):
        return (
            get_all_parsing_errors(m)
            + get_all_enum_errors(m)
            + get_all_data_errors(m)
            + get_all_usecase_errors(m)
            + get_all_model_errors(m)
            + get_all_extension_errors(m)
        )

    return list(flatten(map(collect_errors, model.values())))


def get_all_parsing_errors(model: dict) -> list:
    """Return all parsing errors."""
    # TODO: Make sure there is only one key in the model.
    # => Not sure if we really need this check, to be honest.

    # TODO: Make sure the root name is a valid root name based on the spec.
    def get_unrecognized_root_errors(root):
        if root not in util.get_roots():
            return "{} is not a recognized AaC root type".format(root)
        return ""

    # TODO: Make sure the model is valid per it's spec type.
    # That is, if we're trying to validate a data model, then make sure we
    # validate against the data model spec.
    # => I think, we're basically doing this with each of the get_all_*_errors functions.

    # TODO: Make sure all types are defined somewhere in the model.
    # TODO: -> validate references to primitive types
    # TODO: -> validate references to enum values
    # TODO: -> validate references to other models

    return filter_out_empty_strings(map(get_unrecognized_root_errors, model.keys()))


def get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL.

    Return a list of all the validation errors found for the enumeration MODEL.
    If the enumeration MODEL is valid, return an empty list.
    """

    def is_enum_model(model):
        return "enum" in model

    if is_enum_model(model):
        return get_all_errors_for(model, kind="enum", items=ENUM_ITEMS)

    return []


def get_all_errors_for(model: dict, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    model = model[properties["kind"]] if "kind" in properties else model
    items = properties["items"]

    props = [i["name"] for i in items]
    types = [i["type"] for i in items]
    required = [i["name"] for i in items if i["required"]]

    return filter_out_empty_strings(
        get_all_errors_if_missing_required_properties(model, required),
        get_all_errors_if_properties_have_wrong_type(model, props, types),
        get_all_errors_if_unrecognized_properties(model, props),
    )


def filter_out_empty_strings(*xs: list) -> list:
    """Return XS with all empty strings removed."""
    return list(filter(lambda x: x != "", flatten(xs)))


def get_all_errors_if_missing_required_properties(model: dict, required: list) -> iter:
    """Get error messages if the model is missing required properties.

    Return an iterable object containing any error messages for all REQUIRED
    properties that are not present in the MODEL. If the MODEL has all of the
    required properties, the returned collection will be empty.
    """

    def get_error_if_missing_required_property(key):
        if key not in model.keys():
            return f"missing required field '{key}' in model '{model}'"
        return ""

    return map(get_error_if_missing_required_property, required)


def get_all_errors_if_properties_have_wrong_type(model: dict, names: list, types: list) -> iter:
    """Get error messages if the model has required fields of the wrong type.

    Return an iterable object containing any error messages for all PROPS that
    are not the permitted type in the MODEL. If the MODEL's required fields are
    all of the correct type, the returned collection will be empty.
    """

    def get_error_if_property_has_wrong_type(key, instance):
        if key in model.keys() and not isinstance(model[key], instance):
            return f"unrecognized type for field '{key}' in model '{model}'"
        return ""

    return map(get_error_if_property_has_wrong_type, names, types)


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
        return ""

    return map(get_error_if_property_is_unrecognized, model.keys())


def get_all_data_errors(model: dict) -> list:
    """Return all validation errors for the data MODEL.

    Return a list of all the validation errors found for the data MODEL. If the
    data MODEL is valid, return an empty list.
    """

    def is_data_model(model):
        return "data" in model

    if is_data_model(model):
        data = model["data"]
        return filter_out_empty_strings(
            get_all_errors_for(model, kind="data", items=DATA_ITEMS),
            get_all_non_root_element_errors(data, "fields", list, FIELD_ITEMS),
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
        return ""

    if has_required_fields(model):
        return filter_out_empty_strings(map(get_required_field_error, model["required"]))

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
        return filter_out_empty_strings(
            get_all_errors_for(model, kind="usecase", items=USECASE_ITEMS),
            get_all_non_root_element_errors(usecase, "participants", list, FIELD_ITEMS),
            get_all_non_root_element_errors(usecase, "steps", list, STEP_ITEMS),
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
        return filter_out_empty_strings(
            get_all_errors_for(model, kind="model", items=MODEL_ITEMS),
            get_all_non_root_element_errors(m, "behavior", list, BEHAVIOR_ITEMS),
            get_all_non_root_element_errors(m, "components", list, FIELD_ITEMS),
            get_all_non_root_element_errors(behaviors, "acceptance", list, SCENARIO_ITEMS),
            get_all_non_root_element_errors(behaviors, "input", list, FIELD_ITEMS),
            get_all_non_root_element_errors(behaviors, "output", list, FIELD_ITEMS),
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
            ("dataExt", dict, DATA_EXTENSION_ITEMS)
            if is_data_ext(ext)
            else ("enumExt", dict, ENUM_EXTENSION_ITEMS)
        )
        return filter_out_empty_strings(
            get_all_errors_for(model, kind="ext", items=EXTENSION_ITEMS),
            get_all_errors_if_data_and_enum_extension_combined(ext),
            get_all_non_root_element_errors(ext, kind, type, items),
            # TODO: Not generic enough
            get_all_non_root_element_errors(ext[kind], "add", list, FIELD_ITEMS)
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
        return field["name"] in values["required"]

    def add_required_value_to_field(field):
        return field | {"required": is_required_field(field)}

    return list(map(add_required_value_to_field, fields))


# TODO: Eventually, this should come from the AaC.yaml file

ENUM_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "values", "type": list, "required": True},
]

DATA_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "fields", "type": list, "required": True},
    {"name": "required", "type": list, "required": False},
]

FIELD_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "type", "type": str, "required": True},
]

USECASE_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "description", "type": str, "required": False},
    {"name": "participants", "type": list, "required": True},
    {"name": "steps", "type": list, "required": True},
]

STEP_ITEMS = [
    {"name": "step", "type": str, "required": False},
    {"name": "source", "type": str, "required": False},
    {"name": "target", "type": str, "required": False},
    {"name": "action", "type": str, "required": False},
    {"name": "if", "type": dict, "required": False},
    {"name": "else", "type": dict, "required": False},
    {"name": "loop", "type": dict, "required": False},
]

MODEL_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "description", "type": str, "required": False},
    {"name": "components", "type": list, "required": False},
    {"name": "behavior", "type": list, "required": True},
]

BEHAVIOR_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "type", "type": Enum, "required": True},
    {"name": "description", "type": str, "required": False},
    {"name": "tags", "type": list, "required": False},
    {"name": "input", "type": list, "required": False},
    {"name": "output", "type": list, "required": False},
    {"name": "acceptance", "type": list, "required": True},
]

SCENARIO_ITEMS = [
    {"name": "scenario", "type": str, "required": True},
    {"name": "tags", "type": list, "required": False},
    {"name": "given", "type": list, "required": False},
    {"name": "when", "type": list, "required": True},
    {"name": "then", "type": list, "required": True},
]

EXTENSION_ITEMS = [
    {"name": "name", "type": str, "required": True},
    {"name": "type", "type": str, "required": True},
    {"name": "enumExt", "type": dict, "required": False},
    {"name": "dataExt", "type": dict, "required": False},
]

DATA_EXTENSION_ITEMS = [
    {"name": "add", "type": list, "required": True},
    {"name": "required", "type": list, "required": False},
]

ENUM_EXTENSION_ITEMS = [
    {"name": "add", "type": list, "required": True},
]
