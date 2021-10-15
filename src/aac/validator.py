from iteration_utilities import flatten

from aac import util


def is_valid(model: dict) -> bool:
    """Check if MODEL is valid per the AaC DSL.

    :return: Return True if MODEL is valid; False, otherwise.
    """
    return len(get_all_errors(model)) == 0


def get_all_errors(model: dict) -> list:
    """Return all validation errors for MODEL.

    :return: Return a list of all the validation errors found for MODEL. If the MODEL is valid,
    return an empty list.
    """
    return get_all_enum_errors(model) + get_all_data_errors(model)


def get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL.

    :return: Return a list of all the validation errors found for the enumeration MODEL. If the
    enumeration MODEL is valid, return an empty list.
    """
    if not is_enum_model(model):
        return []

    enum = model["enum"]
    required_properties = ["name", "values"]
    property_types = [str, list]

    property_errors = map(
        lambda p: get_error_if_missing_required_property(enum, p), required_properties
    )
    type_errors = map(
        lambda p, t: get_error_if_property_has_wrong_type(enum, p, t),
        required_properties,
        property_types,
    )

    return filter_out_empty_strings(property_errors, type_errors)


def is_enum_model(model: dict) -> bool:
    """Determine if the MODEL represents an enumeration model."""
    return "enum" in model


def get_error_if_missing_required_property(model: dict, key: str) -> str:
    """Return an error message if the model is missing the specifed property."""
    if key not in model.keys():
        return 'missing required field property: "{}"'.format(key)
    return ""


def get_error_if_property_has_wrong_type(model: dict, key: str, instance: type) -> str:
    if key in model.keys() and not isinstance(model[key], instance):
        return 'wrong type for field property: "{}"'.format(key)
    return ""


def filter_out_empty_strings(*xs: list) -> list:
    """Return XS with all empty strings removed."""
    return list(filter(lambda x: x != "", flatten(xs)))


def get_all_data_errors(model: dict) -> list:
    if not is_data_model(model):
        return []

    data = model["data"]
    required_properties = ["name", "fields"]
    property_types = [str, list]

    property_errors = map(
        lambda p: get_error_if_missing_required_property(data, p), required_properties
    )
    type_errors = map(
        lambda p, t: get_error_if_property_has_wrong_type(data, p, t),
        required_properties + ["required"],
        property_types + [list],
    )

    return filter_out_empty_strings(property_errors, type_errors)


def is_data_model(model: dict) -> bool:
    """Determine if the MODEL represents a data model."""
    return "data" in model
