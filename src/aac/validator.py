"""Validate a model per the AaC DSL."""

# TODO: Replace "magic strings" with a more maintainable solution
# TODO: Generalize get_all_errors to handle all (or at least most of) the cases

from typing import Union

from iteration_utilities import flatten

from aac import util

VALID_TYPES = []


def is_valid(model: dict) -> bool:
    """Check if MODEL is valid per the AaC spec.

    Args:
        model: The model to validate.

    Returns:
        Returns True if the model is valid per the AaC spec; false otherwise.
    """
    return len(validate_and_get_errors(model)) == 0


def validate_and_get_errors(model: dict) -> list:
    """Return all validation errors for MODEL.

    Args:
        model: The model to validate.

    Returns:
        Returns a list of all errors found when validating the model. If the
        model is valid (i.e. there are no errors) an empty list is returned.
    """

    def collect_errors(model):
        actual_model = dict(list(model.values())[0])
        kind = actual_model["name"] if "name" in actual_model else ""
        return (
            _get_all_parsing_errors(model)
            + _get_all_enum_errors(model)
            + _get_all_data_errors(model)
            + _get_all_usecase_errors(model)
            + _get_all_model_errors(model)
            + _get_all_extension_errors(model)
            + _get_all_cross_reference_errors(kind, model)
        )

    return _apply_extensions(model) + list(flatten(map(collect_errors, model.values())))


def _apply_extensions(model):
    errors = []
    aac_data, aac_enums = util.get_aac_spec()
    for ext in util.get_models_by_type(model, "ext"):
        extension = model[ext]
        if not _can_apply_extension(extension):
            errors.append(f"unrecognized extension type {extension}")
            continue

        ext = extension["ext"]
        type_to_extend = ext["type"]
        if type_to_extend in aac_data or type_to_extend in aac_enums:
            errors.append(_apply_extension(ext, aac_data, aac_enums))
        else:
            errors.append(
                _apply_extension(
                    ext,
                    util.get_models_by_type(model, "data"),
                    util.get_models_by_type(model, "enum"),
                )
            )

    return _filter_none_values(errors)


def _can_apply_extension(extension):
    return "ext" in extension and "type" in extension["ext"] and extension["ext"]["type"] != ""


def _apply_extension(extension, data, enums):
    type_to_extend = extension["type"]
    if not _is_enum_ext(extension) and not _is_data_ext(extension):
        return f"unrecognized extension type {type_to_extend}"

    d, name, items, ext_type = (
        (enums, "enum", "values", "enumExt")
        if _is_enum_ext(extension)
        else (data, "data", "fields", "dataExt")
    )
    updated_values = d[type_to_extend][name][items] + extension[ext_type]["add"]
    d[type_to_extend][name][items] = updated_values

    if _is_data_ext(extension) and "required" in extension["dataExt"]:
        updated_required = d[type_to_extend][name]["required"] + extension[ext_type]["required"]
        d[type_to_extend][name][items] = updated_required


def _is_data_ext(model):
    return "dataExt" in model and isinstance(model["dataExt"], dict)


def _is_enum_ext(model):
    return "enumExt" in model and isinstance(model["enumExt"], dict)


def _get_all_parsing_errors(model: dict) -> list:
    """Return all parsing errors."""

    def get_unrecognized_root_errors(root):
        if root not in util.get_roots():
            return f"{root} is not a recognized AaC root type"

    return _filter_none_values(map(get_unrecognized_root_errors, model.keys()))


def _get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL."""

    def is_enum_model(model):
        return kind in model

    kind = "enum"
    if is_enum_model(model):
        return _get_all_errors_for(model, kind=kind, fields=_load_aac_fields_for(kind))

    return []


def _get_all_errors_for(model: dict, **properties) -> list:
    """Get all model errors for the specified kind of model."""
    model = model[properties["kind"]] if "kind" in properties else model
    fields = properties["fields"]

    props = [f["name"] for f in fields]
    required = [f["name"] for f in fields if f["required"]]

    return _filter_none_values(
        _get_all_errors_if_missing_required_properties(model, required),
        _get_all_errors_if_unrecognized_properties(model, props),
    )


def _filter_none_values(*xs: list) -> list:
    """Return XS without None values."""
    return list(filter(lambda x: x, flatten(xs)))


def _get_all_errors_if_missing_required_properties(model: dict, required: list) -> iter:
    """Get error messages if the model is missing required properties."""

    def get_error_if_missing_required_property(key):
        if key not in model.keys():
            return f"missing required field '{key}' in model '{model}'"

    return map(get_error_if_missing_required_property, required)


def _get_all_cross_reference_errors(kind: str, model: dict) -> iter:
    """Validate all cross references."""

    _set_valid_types({kind: model})

    data, enums = util.get_aac_spec()
    models = {kind: model} | data | enums

    data = util.get_models_by_type(models, "data")
    enums = util.get_models_by_type(models, "enum")
    models = util.get_models_by_type(models, "model")
    return list(
        flatten(
            _filter_none_values(
                _validate_data_references(data),
                _validate_model_references(models, data),
                _validate_enum_references(models, data, enums),
            )
        )
    )


def _set_valid_types(model: dict) -> None:
    """Initialize the list of valid types."""
    global VALID_TYPES

    data, enums = util.get_aac_spec()
    VALID_TYPES = list((model | data | enums).keys()) + util.get_primitives()


def _get_error_messages_if_invalid_type(name: str, types: list) -> list:
    """Get a list of error messages if any types are unrecognized."""
    return [f"unrecognized type {t} used in {name}" for t in types if _is_valid_type(t)]


def _is_valid_type(type: str) -> bool:
    """Determine whether the type is valid, or not."""
    return type.strip("[]") not in VALID_TYPES


def _validate_data_references(data: dict) -> list:
    """Ensure all references in data models are valid."""
    fn = lambda name, spec: _get_error_messages_if_invalid_type(
        name, util.search(spec, ["data", "fields", "type"])
    )
    return list(map(fn, data.keys(), data.values()))


def _validate_model_references(models: list, data: dict) -> list:
    """Ensure all references in sysetm models are valid."""
    fn = lambda name, spec: _get_error_messages_if_invalid_type(
        name,
        util.search(spec, ["model", "components", "type"])
        + util.search(spec, ["model", "behavior", "input", "type"])
        + util.search(spec, ["model", "behavior", "output", "type"]),
    )
    return list(map(fn, data.keys(), data.values()))


def _get_enum_paths(data: dict, enums: dict) -> dict:
    """Get the paths to enum values in models."""
    paths = [
        (e, _find_paths_to_enum_fields(e, "model", "model", data, enums))
        for e in enums
        if e != "Primitives"
    ]
    return dict(paths)


def _get_errors_if_model_references_bad_enum_value(
    models: list, enum: str, paths: list, valid: list
) -> list:
    """Return error messages for any enum value that is referenced but not recognized."""

    def get_errors_for_bad_enum_in_model(model, paths):
        errors = []
        for path in paths:
            errors += [
                f"unrecognized '{enum}' value '{result}' in '{model}' at '{' -> '.join(path)}': {valid}"
                for result in util.search(models[model], path)
                if result not in valid
            ]
        return errors

    return list(flatten(map(lambda m: get_errors_for_bad_enum_in_model(m, paths), models)))


def _validate_enum_references(models: list, data: dict, enums: dict) -> list:
    """Validate all references to enum fields in all models."""
    enum_paths = _get_enum_paths(data, enums)
    paths = list(enum_paths.values())[0]
    return [
        _get_errors_if_model_references_bad_enum_value(
            models, e, paths, util.search(enums[e], ["enum", "values"])
        )
        for e in enum_paths
    ]


def _get_enum_fields(enum: str, fields: list, data: dict, enums: dict) -> list:
    """Get all fields in models that are of the desired type."""
    enum_fields = []
    for field in fields:
        field_type = field["type"].strip("[]")
        if field_type in enums.keys():
            if field_type == enum:
                enum_fields.append([field["name"]])
        elif field_type not in util.get_primitives():
            found_paths = _find_paths_to_enum_fields(enum, field["name"], field_type, data, enums)
            for found in found_paths:
                entry = found.copy()
                enum_fields.append(entry)
    return enum_fields


def _find_paths_to_enum_fields(find_enum, data_name, data_type, data, enums):
    """Return the paths to any references to enum fields in models."""
    fields = util.search(data[data_type], ["data", "fields"])
    return map(
        lambda enum: [data_name] + enum,
        _get_enum_fields(find_enum, fields, data, enums),
    )


def _get_all_errors_if_unrecognized_properties(model: dict, props: list) -> iter:
    """Get error messages if the model has unrecognized properties."""

    def get_error_if_property_is_unrecognized(key):
        if key not in props:
            return f"unrecognized field named '{key}' found in model '{model}'"

    return map(get_error_if_property_is_unrecognized, model.keys())


def _get_all_data_errors(model: dict) -> list:
    """Return all validation errors for the data MODEL."""

    def is_data_model(model):
        return kind in model

    kind = "data"
    if is_data_model(model):
        data = model[kind]
        return _filter_none_values(
            _get_all_errors_for(model, kind=kind, fields=_load_aac_fields_for(kind)),
            _get_all_non_root_element_errors(data, "fields", list, _load_aac_fields_for("Field")),
            _get_all_required_field_errors(data),
        )

    return []


def _get_all_non_root_element_errors(
    model: Union[dict, list], element: str, type: type, fields: list
) -> list:
    """Return all validation errors for the non-root element MODELs."""

    def has_element(model):
        return element in model and isinstance(model[element], type)

    def get_field_errors(model):
        if has_element(model):
            model = [model[element]] if isinstance(model[element], dict) else model[element]
            return flatten(map(lambda x: _get_all_errors_for(x, fields=fields), model))
        return []

    model = model if isinstance(model, list) else [model]
    return flatten(map(get_field_errors, model))


def _get_all_required_field_errors(model: dict) -> list:
    """Return all validation errors for the required fields of the MODEL."""

    def has_required_fields(model: dict):
        return "required" in model and isinstance(model["required"], list)

    def get_required_field_error(required):
        if required not in map(lambda f: f["name"], model["fields"]):
            return f"reference to undefined required field: {required}"

    if has_required_fields(model):
        return _filter_none_values(map(get_required_field_error, model["required"]))

    return []


def _get_all_usecase_errors(model: dict) -> list:
    """Return all validation errors for the usecase MODEL."""

    def is_usecase(model):
        return "usecase" in model

    if is_usecase(model):
        usecase = model["usecase"]
        return _filter_none_values(
            _get_all_errors_for(model, kind="usecase", fields=_load_aac_fields_for("usecase")),
            _get_all_non_root_element_errors(
                usecase, "participants", list, _load_aac_fields_for("Field")
            ),
            _get_all_non_root_element_errors(usecase, "steps", list, _load_aac_fields_for("Step")),
        )

    return []


def _get_all_model_errors(model: dict) -> list:
    """Return all validation errors for the system MODEL."""

    def is_model(model):
        return "model" in model

    def has_behaviors(model):
        return "behavior" in model and isinstance(model["behavior"], list)

    if is_model(model):
        m = model["model"]
        behaviors = m["behavior"] if has_behaviors(m) else []
        return _filter_none_values(
            _get_all_errors_for(model, kind="model", fields=_load_aac_fields_for("model")),
            _get_all_non_root_element_errors(
                m, "behavior", list, _load_aac_fields_for("Behavior")
            ),
            _get_all_non_root_element_errors(m, "components", list, _load_aac_fields_for("Field")),
            _get_all_non_root_element_errors(
                behaviors, "acceptance", list, _load_aac_fields_for("Scenario")
            ),
            _get_all_non_root_element_errors(
                behaviors, "input", list, _load_aac_fields_for("Field")
            ),
            _get_all_non_root_element_errors(
                behaviors, "output", list, _load_aac_fields_for("Field")
            ),
        )

    return []


def _get_all_extension_errors(model: dict) -> list:
    """Return all validation errors for the system MODEL."""

    def is_ext(model):
        return "ext" in model

    def get_all_errors_if_data_and_enum_extension_combined(model):
        if _is_data_ext(model) and _is_enum_ext(model):
            return ["cannot combine enumExt and dataExt in the same extension"]
        return []

    if is_ext(model):
        ext = model["ext"]
        kind, type, items = (
            ("dataExt", dict, _load_aac_fields_for("DataExtension"))
            if _is_data_ext(ext)
            else ("enumExt", dict, _load_aac_fields_for("EnumExtension"))
        )
        return _filter_none_values(
            _get_all_errors_for(model, kind="ext", fields=_load_aac_fields_for("extension")),
            get_all_errors_if_data_and_enum_extension_combined(ext),
            _get_all_non_root_element_errors(ext, kind, type, items),
            # TODO: Not generic enough
            _get_all_non_root_element_errors(ext[kind], "add", list, _load_aac_fields_for("Field"))
            if _is_data_ext(ext)
            else [],
        )

    return []


def _load_aac_fields_for(kind: str) -> list:
    """Get the AaC fields and their properties for the specified KIND of item."""
    data, _ = util.get_aac_spec()
    values = data[kind]["data"]
    fields = values["fields"]

    def is_required_field(field):
        return "required" in values and field["name"] in values["required"]

    def add_required_value_to_field(field):
        return field | {"required": is_required_field(field)}

    return list(map(add_required_value_to_field, fields))
