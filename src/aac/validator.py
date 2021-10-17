"""Validate a model per the AaC DSL."""

# TODO: Replace "magic strings" with a more maintainable solution
# TODO: Generalize get_all_errors to handle all (or at least most of) the cases

from iteration_utilities import flatten


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
        return get_all_enum_errors(m) + get_all_data_errors(m) + get_all_usecase_errors(m)

    return list(flatten(map(collect_errors, model.values())))


def get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL.

    Return a list of all the validation errors found for the enumeration MODEL.
    If the enumeration MODEL is valid, return an empty list.
    """

    def is_enum_model(model):
        return "enum" in model

    if is_enum_model(model):
        return get_all_model_errors(model, kind="enum", items=ENUM_ITEMS)

    return []


def get_all_model_errors(model: dict, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    m = model[properties["kind"]] if "kind" in properties else model
    items = [dict(i.items()) for i in properties["items"]]

    props = [i["name"] for i in items]
    types = [i["type"] for i in items]
    required = [i["name"] for i in items if i["required"]]

    return filter_out_empty_strings(
        get_all_errors_if_missing_required_properties(m, required),
        get_all_errors_if_properties_have_wrong_type(m, props, types),
        get_all_errors_if_unrecognized_properties(m, props),
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
            return 'missing required field property: "{}"'.format(key)
        return ""

    return map(get_error_if_missing_required_property, required)


def get_all_errors_if_properties_have_wrong_type(model: dict, props: list, types: list) -> iter:
    """Get error messages if the model has required properties of the wrong type.

    Return an iterable object containing any error messages for all PROPS that
    are not the permitted type in the MODEL. If the MODEL's required properties
    are all of the correct type, the returned collection will be empty.
    """

    def get_error_if_property_has_wrong_type(key, instance):
        if key in model.keys() and not isinstance(model[key], instance):
            return 'wrong type for field property: "{}"'.format(key)
        return ""

    return map(get_error_if_property_has_wrong_type, props, types)


def get_all_errors_if_unrecognized_properties(model: dict, props: list) -> iter:
    """Get error messages if the model has unrecognized properties.

    Return an iterable object containing any error messages for all properties
    found in the MODEL that are not recognized as valid for the specified model.
    If the MODEL's has no unrecognized properties, the returned collection will
    be empty.
    """

    def get_error_if_property_is_unrecognized(key):
        if key not in props:
            return 'unrecognized property: "{}"'.format(key)
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
            get_all_model_errors(model, kind="data", items=DATA_ITEMS),
            get_all_non_root_element_errors(data, "fields", FIELD_ITEMS),
            get_all_required_field_errors(data),
        )

    return []


# TODO: items is a horrible name, here, find a better one
def get_all_non_root_element_errors(model: dict, element: str, items: list) -> list:
    """Return all validation errors for the field MODEL.

    Return a list of all the validation errors found for the field MODEL. If the
    field MODEL is valid, return an empty list.
    """

    def has_element(model):
        return element in model and isinstance(model[element], list)

    def get_field_error(field):
        return get_all_model_errors(field, items=items)

    if has_element(model):
        return flatten(map(get_field_error, model[element]))

    return []


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
    """Return all parsing errors for the MODEL.

    Return a list of general parsing errors for the MODEL. If the MODEL is valid,
    return an empty list.
    """

    def is_usecase(model):
        return "usecase" in model

    if is_usecase(model):
        usecase = model["usecase"]
        return filter_out_empty_strings(
            get_all_model_errors(model, kind="usecase", items=USECASE_ITEMS),
            get_all_non_root_element_errors(usecase, "participants", FIELD_ITEMS),
            get_all_non_root_element_errors(usecase, "steps", STEP_ITEMS),
        )

    return []


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
