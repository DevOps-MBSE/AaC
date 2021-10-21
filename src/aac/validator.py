"""Validate a model per the AaC DSL."""

# TODO: Replace "magic strings" with a more maintainable solution
# TODO: Generalize get_all_errors to handle all (or at least most of) the cases

from typing import Union

from iteration_utilities import flatten

from aac import util

VALID_TYPES = []


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

    fn = lambda m: list(flatten(map(collect_errors, m.values())))
    return list(flatten(map(fn, model))) if isinstance(model, list) else fn(model)


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
        return get_all_errors_for(model, kind=kind, fields=load_aac_fields_for(kind))

    return []


def get_all_errors_for(model: dict, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    model = model[properties["kind"]] if "kind" in properties else model
    fields = properties["fields"]

    props = [f["name"] for f in fields]
    types = [f["type"] for f in fields]
    required = [f["name"] for f in fields if f["required"]]

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


def get_all_cross_reference_errors(kind: str, model: dict) -> iter:
    """Validate all cross references.

    Returns:
      Returns an iterable object that contains all error messages related to
      unrecognized cross-references in a model.
    """

    set_valid_types({kind: model})

    data, enums = util.get_aac_spec()
    models = {kind: model} | data | enums

    data = util.get_models_by_type(models, "data")
    enums = util.get_models_by_type(models, "enum")
    models = util.get_models_by_type(models, "model")
    return list(
        flatten(
            filter_none_values(
                validate_data_references(data),
                validate_model_references(models, data),
                validate_enum_references(models, data, enums),
            )
        )
    )


def set_valid_types(model: dict) -> None:
    """Initialize the list of valid types."""
    global VALID_TYPES

    data, enums = util.get_aac_spec()
    VALID_TYPES = list((model | data | enums).keys()) + util.get_primitives()


def get_error_messages_if_invalid_type(name: str, types: list) -> list:
    """Get a list of error messages if any types are unrecognized."""
    return [f"unrecognized type {t} used in {name}" for t in types if is_valid_type(t)]


def is_valid_type(type: str) -> bool:
    """Determine whether the type is valid, or not."""
    return type.strip("[]") not in VALID_TYPES


def validate_data_references(data: dict) -> list:
    """Ensure all references in data models are valid."""
    fn = lambda name, spec: get_error_messages_if_invalid_type(
        name, util.search(spec, ["data", "fields", "type"])
    )
    return list(map(fn, data.keys(), data.values()))


def validate_model_references(models: list, data: dict) -> list:
    """Ensure all references in sysetm models are valid."""
    fn = lambda name, spec: get_error_messages_if_invalid_type(
        name,
        util.search(spec, ["model", "components", "type"])
        + util.search(spec, ["model", "behavior", "input", "type"])
        + util.search(spec, ["model", "behavior", "output", "type"]),
    )
    return list(map(fn, data.keys(), data.values()))


def get_enum_paths(data: dict, enums: dict) -> dict:
    """Get the paths to enum values in models."""
    paths = [
        (e, find_paths_to_enum_fields(e, "model", "model", data, enums))
        for e in enums
        if e != "Primitives"
    ]
    return dict(paths)


def get_errors_if_model_references_bad_enum_value(
    models: list, enum: str, paths: list, valid: list
) -> list:
    """Return error messages for any enum value that is referenced but not recognized."""

    def get_errors_for_bad_enum_in_model(model, paths):
        errors = []
        for path in paths:
            errors += [
                f"Model {model} entry {path} has a value {result} not allowed in the enumeration {enum}: {valid}"
                for result in util.search(models[model], path)
                if result not in valid
            ]
        return errors

    return list(flatten(map(lambda m: get_errors_for_bad_enum_in_model(m, paths), models)))


def validate_enum_references(models: list, data: dict, enums: dict) -> list:
    """Validate all references to enum fields in all models."""
    valid_values = []
    enum_paths = get_enum_paths(data, enums)
    paths = list(enum_paths.values())[0]
    return [
        get_errors_if_model_references_bad_enum_value(
            models, e, paths, util.search(enums[e], ["enum", "values"])
        )
        for e in enum_paths
    ]


def get_enum_fields(enum: str, fields: list, data: dict, enums: dict) -> list:
    """Get all fields in models that are of the desired type."""
    enum_fields = []
    for field in fields:
        field_type = field["type"].strip("[]")
        if field_type in enums.keys():
            if field_type == enum:
                enum_fields.append([field["name"]])
        elif field_type not in util.get_primitives():
            found_paths = find_paths_to_enum_fields(enum, field["name"], field_type, data, enums)
            for found in found_paths:
                entry = found.copy()
                enum_fields.append(entry)
    return enum_fields


def find_paths_to_enum_fields(find_enum, data_name, data_type, data, enums):
    """Return the paths to any references to enum fields in models."""
    fields = util.search(data[data_type], ["data", "fields"])
    return map(
        lambda enum: [data_name] + enum,
        get_enum_fields(find_enum, fields, data, enums),
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
            get_all_errors_for(model, kind=kind, fields=load_aac_fields_for(kind)),
            get_all_non_root_element_errors(data, "fields", list, load_aac_fields_for("Field")),
            get_all_required_field_errors(data),
        )

    return []


def get_all_non_root_element_errors(
    model: Union[dict, list], element: str, type: type, fields: list
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
            return flatten(map(lambda x: get_all_errors_for(x, fields=fields), model))
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
            get_all_errors_for(model, kind="usecase", fields=load_aac_fields_for("usecase")),
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
            get_all_errors_for(model, kind="model", fields=load_aac_fields_for("model")),
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
            get_all_errors_for(model, kind="ext", fields=load_aac_fields_for("extension")),
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
