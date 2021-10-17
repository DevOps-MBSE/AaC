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
        return get_all_model_errors(
            model,
            kind="enum",
            items=[
                {"name": "name", "type": str, "required": True},
                {"name": "values", "type": list, "required": True},
            ],
        )

    return []


def get_all_model_errors(model: dict, kind: str, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    items = [dict(i.items()) for i in properties["items"]]

    props = [i["name"] for i in items]
    types = [i["type"] for i in items]
    required = [i["name"] for i in items if i["required"]]

    return filter_out_empty_strings(
        get_all_errors_if_missing_required_properties(model[kind], required),
        get_all_errors_if_properties_have_wrong_type(model[kind], props, types),
        get_all_errors_if_unrecognized_properties(model[kind], props),
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
    if not is_data_model(model):
        return []

    data = model["data"]
    required = ["name", "fields"]
    types = [str, list]

    return filter_out_empty_strings(
        get_all_errors_if_missing_required_properties(data, required),
        get_all_errors_if_properties_have_wrong_type(
            data, required + ["required"], types + [list]
        ),
        get_all_field_errors(data),
        get_all_required_field_errors(data),
    )


def is_data_model(model: dict) -> bool:
    """Determine if the MODEL represents a data model."""
    return "data" in model


def get_all_field_errors(model: dict) -> list:
    """Return all validation errors for the field MODEL.

    Return a list of all the validation errors found for the field MODEL. If the
    field MODEL is valid, return an empty list.
    """
    if not has_fields(model):
        return []

    def get_field_error(field):
        required = ["name", "type"]
        types = [str, str]

        # TODO: Clean this up
        return filter_out_empty_strings(
            list(get_all_errors_if_missing_required_properties(field, required)),
            list(get_all_errors_if_properties_have_wrong_type(field, required, types)),
        )

    return flatten(map(get_field_error, model["fields"]))


def has_fields(model: dict) -> bool:
    """Determine if the MODEL represents a field."""
    return "fields" in model and isinstance(model["fields"], list)


def get_all_required_field_errors(model: dict) -> list:
    """Return all validation errors for the required fields of the MODEL.

    Return a list of all the validation errors found for the required fields of
    the MODEL. If the required field of the MODEL is valid, return an empty
    list.
    """
    if not has_required_fields(model):
        return []

    def get_required_field_error(required):
        if required not in map(lambda f: f["name"], model["fields"]):
            return "reference to undefined required field: {}".format(required)
        return ""

    return filter_out_empty_strings(map(get_required_field_error, model["required"]))


def has_required_fields(model: dict):
    """Determine if the MODEL has required fields."""
    return "required" in model and isinstance(model["required"], list)


def get_all_usecase_errors(model: dict) -> list:
    """Return all parsing errors for the MODEL.

    Return a list of general parsing errors for the MODEL. If the MODEL is valid,
    return an empty list.
    """
    if not is_usecase(model):
        return []

    usecase = model["usecase"]
    required = ["name", "participants", "steps"]
    types = [str, list, list]
    return filter_out_empty_strings(
        get_all_errors_if_missing_required_properties(usecase, required),
        get_all_errors_if_properties_have_wrong_type(
            usecase, required + ["description"], types + [str]
        ),
    )


def is_usecase(model):
    """Determine if the MODEL represents a usecase."""
    return "usecase" in model
