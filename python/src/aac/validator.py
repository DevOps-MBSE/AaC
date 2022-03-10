"""Validate a model per the AaC DSL."""

import copy
from contextlib import contextmanager
from typing import Union

from attr import attrib, attrs, validators, Factory
from iteration_utilities import flatten

from aac import plugins, util
from aac.parser import ParsedModel
from aac.spec.core import get_aac_spec, get_primitives

VALIDATOR_CONTEXT = None


class ValidationError(RuntimeError):
    """An error that represents a model with invalid components and/or structure."""

    pass


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of validating a model.

    Attributes:
        messages (list[str]): A list of messages to be provided as feedback for the user.
        model (ParsedModel): The model that was validated; if the model is invalid, None.
    """

    parsed_model: ParsedModel = attrib(validator=validators.instance_of(ParsedModel))
    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))


@contextmanager
def validation(model_producer: callable, source: str, **kwargs):
    """Run validation on the model returned by func.

    Args:
        model_producer (callable): A function that returns an Architecture-as-Code model. The
                                       first argument accepted by model_producer must be the source
                                       of the YAML representation of the model.
        source (str): The source of the YAML representation of the model.
        kwargs (dict): Any additional arguments that should be passed on to model_producer.

    Returns:
        If the model returned by model_producer is valid, it is returned. Otherwise, None is returned.
    """
    try:
        result = ValidationResult(model_producer(source))
        _validate(result.parsed_model.model)
        result.messages.append(f"{source} is valid")
        yield result
    except ValidationError as ve:
        raise ValidationError(source, *ve.args)


def _validate(model: dict) -> None:
    """Return all validation errors for the model.

    This function validates the target model against the core AaC Spec and any actively installed
    plugin data, enum, and extension definitions.

    Args:
        model: The model to validate.

    Raises:
        Raises a ValidationError if any errors are found when validating the model.
    """
    global VALIDATOR_CONTEXT

    if not VALIDATOR_CONTEXT:
        aac_enum, aac_data = get_aac_spec()
        VALIDATOR_CONTEXT = ValidatorContext(aac_enum | aac_data, {}, plugins.get_plugin_model_definitions(), model)

    try:
        errors = list(flatten(map(_validate_model, model.values())))
    finally:
        # Once we're done validating, wipe the context.
        VALIDATOR_CONTEXT = None

    if errors:
        raise ValidationError(model, errors)


def _validate_model(model: dict) -> list:
    """Validate a model by checking that it meets the requirements to be considered valid, and return any errors if it's invalid."""
    actual_model = list(model.values())[0]
    name = actual_model.get("name") or ""
    errors = (
        _get_all_parsing_errors(model)
        + _get_all_enum_errors(model)
        + _get_all_data_errors(model)
        + _get_all_usecase_errors(model)
        + _get_all_model_errors(model)
        + _get_all_extension_errors(model)
        + _get_all_cross_reference_errors(name, model)
    )

    return errors


def _is_data_ext(model):
    return "dataExt" in model and isinstance(model["dataExt"], dict)


def _is_enum_ext(model):
    return "enumExt" in model and isinstance(model["enumExt"], dict)


def _is_ext(model):
    return "ext" in model and isinstance(model["ext"], dict)


def _get_all_parsing_errors(model: dict) -> list:
    """Return all parsing errors."""

    def get_unrecognized_root_errors(root):
        if root not in VALIDATOR_CONTEXT.get_root_type_names():
            return f"{root} is not a recognized AaC root type"

    return _filter_none_values(map(get_unrecognized_root_errors, model.keys()))


def _get_all_enum_errors(model: dict) -> list:
    """Return all validation errors for the enumeration MODEL."""

    def is_enum_model(model):
        return kind in model

    kind = "enum"
    if is_enum_model(model):
        return _get_all_errors_for(model, kind=kind, fields=_load_extended_aac_fields_for(kind))

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

        prop = model.get(key)
        if isinstance(prop, (list, str)) and len(prop) == 0:
            return f"empty {type(prop).__name__} provided for required property '{key}' in model '{model}'"

    return list(map(get_error_if_missing_required_property, required))


def _get_all_cross_reference_errors(kind: str, model: dict) -> iter:
    """Validate all cross references."""
    data = VALIDATOR_CONTEXT.get_all_data_definitions()
    enums = VALIDATOR_CONTEXT.get_all_enum_definitions()
    models = VALIDATOR_CONTEXT.get_all_model_definitions()
    return list(
        flatten(
            _filter_none_values(
                _validate_data_references(data),
                _validate_model_references(models, data),
                _validate_enum_references(models, data, enums),
            )
        )
    )


def _get_error_messages_if_invalid_type(name: str, types: list) -> list:
    """Get a list of error messages if any types are unrecognized."""
    return [f"unrecognized type {t} used in {name}" for t in types if not _is_defined_type(t)]


def _is_defined_type(type: str) -> bool:
    """Determine whether the type is valid, or not."""
    return type.strip("[]") in VALIDATOR_CONTEXT.get_defined_types()


def _validate_data_references(data: dict) -> list:
    """Ensure all references in data models are valid."""

    def fn(name, spec):
        return _get_error_messages_if_invalid_type(
            name, util.search(spec, ["data", "fields", "type"])
        )

    return list(map(fn, data.keys(), data.values()))


def _validate_model_references(models: list, data: dict) -> list:
    """Ensure all references in system models are valid."""

    def fn(name, spec):
        return _get_error_messages_if_invalid_type(
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


def _get_errors_if_model_references_bad_enum_value(models: list, enum: str, paths: list, valid: list) -> list:
    """Return error messages for any enum value that is referenced but not recognized."""

    def get_errors_for_bad_enum_in_model(model):
        errors = []
        for path in paths:
            errors += [
                f"unrecognized '{enum}' value '{result}' in '{model}' at '{' -> '.join(path)}': {valid}"
                for result in util.search(models[model], path)
                if result not in valid
            ]
        return errors

    return list(flatten(map(get_errors_for_bad_enum_in_model, models)))


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

    def get_enum_field(field_name, field_type):
        if field_type in enums.keys():
            if field_type == enum:
                enum_fields.append([field_name])
        elif field_type not in get_primitives():
            found_paths = _find_paths_to_enum_fields(enum, field_name, field_type, data, enums)
            enum_fields.extend([found.copy() for found in found_paths])

    for field in fields:
        get_enum_field(field["name"], field["type"].strip("[]"))

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
            _get_all_errors_for(model, kind=kind, fields=_load_extended_aac_fields_for(kind)),
            _get_all_non_root_element_errors(
                data, "fields", list, _load_extended_aac_fields_for("Field")
            ),
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
            _get_all_errors_for(
                model, kind="usecase", fields=_load_extended_aac_fields_for("usecase")
            ),
            _get_all_non_root_element_errors(
                usecase, "participants", list, _load_extended_aac_fields_for("Field")
            ),
            _get_all_non_root_element_errors(
                usecase, "steps", list, _load_extended_aac_fields_for("Step")
            ),
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
            _get_all_errors_for(
                model, kind="model", fields=_load_extended_aac_fields_for("model")
            ),
            _get_all_non_root_element_errors(
                m, "behavior", list, _load_extended_aac_fields_for("Behavior")
            ),
            _get_all_non_root_element_errors(
                m, "components", list, _load_extended_aac_fields_for("Field")
            ),
            _get_all_non_root_element_errors(
                behaviors, "acceptance", list, _load_extended_aac_fields_for("Scenario")
            ),
            _get_all_non_root_element_errors(
                behaviors, "input", list, _load_extended_aac_fields_for("Field")
            ),
            _get_all_non_root_element_errors(
                behaviors, "output", list, _load_extended_aac_fields_for("Field")
            ),
        )

    return []


def _get_all_extension_errors(model: dict) -> list:
    """Return all validation errors for the system MODEL."""
    if _is_ext(model):
        extension_errors = _is_valid_extension(model) + _is_valid_extension_type(model)
        if extension_errors:
            return extension_errors

        ext = model.get("ext")
        kind, items = (
            ("dataExt", _load_unextended_aac_fields_for("DataExtension"))
            if _is_data_ext(ext)
            else ("enumExt", _load_unextended_aac_fields_for("EnumExtension"))
        )
        return _filter_none_values(
            _get_all_errors_for(model, kind="ext", fields=_load_unextended_aac_fields_for("extension")),
            _get_all_non_root_element_errors(ext, kind, dict, items),
            _get_all_non_root_element_errors(ext[kind], "add", list, _load_unextended_aac_fields_for("Field"))
            if _is_data_ext(ext)
            else [],
        )

    return []


def _is_valid_extension(model):
    """Check that the extension is an extension and has a non-empty type."""

    def get_all_errors_if_data_and_enum_extension_combined(model):
        if _is_data_ext(model) and _is_enum_ext(model):
            return ["cannot combine enumExt and dataExt in the same extension"]
        return []

    def check_for_missing_field(model: dict, fields: list) -> str:
        """Check that the ext and type fields exist in the model and that type is not empty."""
        current_field, *remaining_fields = fields
        if current_field not in model or model.get(current_field) == "":
            return [f"missing required field '{current_field}' in model '{model}'"]
        elif remaining_fields:
            return check_for_missing_field(model.get(current_field), remaining_fields)
        return []

    return check_for_missing_field(model, ["ext", "type"]) + get_all_errors_if_data_and_enum_extension_combined(model.get("ext"))


def _is_valid_extension_type(model):
    """Check that the extension is either a data or enum extension."""
    extension_model = model.get("ext")
    if not (extension_model.get("dataExt") or extension_model.get("enumExt")):
        return [f"unrecognized extension type {model}"]
    return []


def _load_aac_fields_from_models(model_type: str, models: dict) -> list:
    """Get the AaC fields and their properties for the specified KIND of item."""
    data_model = models[model_type]["data"]
    fields = data_model["fields"]

    def is_required_field(field):
        return "required" in data_model and field["name"] in data_model["required"]

    def add_required_value_to_field(field):
        return field | {"required": is_required_field(field)}

    return list(map(add_required_value_to_field, fields))


def _load_extended_aac_fields_for(model_type: str) -> list:
    """Get the AaC fields and their properties for the specified KIND of item."""
    models = VALIDATOR_CONTEXT.get_all_extended_definitions()
    return _load_aac_fields_from_models(model_type, models)


def _load_unextended_aac_fields_for(model_type: str) -> list:
    """Get the AaC fields and their properties for the specified KIND of item."""
    models = VALIDATOR_CONTEXT.get_all_unextended_definitions()
    return _load_aac_fields_from_models(model_type, models)


@attrs(slots=True, auto_attribs=True)
class ValidatorContext:
    """
    A class used to provide access to several disparate AaC model definition sources during the validation process.

    Attributes:
        core_aac_spec_model: A dict of the core AaC spec
        plugin_defined_models: a dict of models, datas, and enums defined via plugins
        plugin_defined_extensions: a dict extensions defined via plugins
        validation_target_models: a dict of models that are being validated.
    """

    parsed_models_type_attribute_settings = {
        "default": {},
        "validator": validators.instance_of(dict),
    }

    core_aac_spec_models: dict = attrib(**parsed_models_type_attribute_settings)
    plugin_defined_models: dict = attrib(**parsed_models_type_attribute_settings)
    plugin_defined_extensions: dict = attrib(**parsed_models_type_attribute_settings)
    validation_target_models: dict = attrib(**parsed_models_type_attribute_settings)

    # These attributes aren't exposed in the constructor, and are intended as private members, but attrs doesn't support private members.
    extended_validation_aac_model: list = attrib(
        validator=validators.instance_of(dict), init=False, default=Factory(dict)
    )

    def get_root_type_names(self) -> list[str]:
        """Get the list of root names as defined in the extended AaC model specification.

        Returns:
            A list of strings, one entry for each root name in the AaC model specification.
        """

        def get_field_name(fields_entry_dict: dict):
            return fields_entry_dict.get("name")

        roots_model = self.get_all_extended_definitions().get("root")

        if roots_model:
            return map(get_field_name, roots_model.get("data").get("fields"))
        else:
            return []

    def get_defined_types(self) -> list[str]:
        """
        Return the complete list of defined types in the validation context.

        Returns:
            List of all defined types in the validation context
        """
        return list(self.get_all_extended_definitions().keys()) + get_primitives()

    def get_all_model_definitions(self):
        """Return all definitions of the 'model' type."""
        return util.get_models_by_type(self.get_all_extended_definitions(), "model")

    def get_all_data_definitions(self):
        """Return all definitions of the 'data' type."""
        return util.get_models_by_type(self.get_all_extended_definitions(), "data")

    def get_all_enum_definitions(self):
        """Return all definitions of the 'enum' type."""
        return util.get_models_by_type(self.get_all_extended_definitions(), "enum")

    def get_all_extended_definitions(self):
        """
        Return all model, data, enum, etc definitions in the context with active plugin extensions and definitions.

        Returns the complete list of plugin-extended definitions available in the context.
            See `get_all_unextended_definitions()` to get the list of definitions without plugin
            extensions applied.

        Returns:
            List of AaC definitions
        """
        definitions = self.get_all_unextended_definitions()
        extensions = util.get_models_by_type(definitions, "ext")

        if not self.extended_validation_aac_model:
            for extension in extensions.values():
                plugin_errors = _get_all_extension_errors(extension)
                if not plugin_errors:
                    target_to_modify = extension["ext"]["type"]
                    self._apply_extension_to_model(definitions[target_to_modify], extension["ext"])

            self.extended_validation_aac_model = definitions

        return self.extended_validation_aac_model

    def get_all_unextended_definitions(self):
        """
        Return all model, data, enum, etc definitions in the context without applying pluggin extensions.

        Returns the complete list of definitions available in the context, including those provided by actively
            installed plugins without applying any plugin extensions to the exsiting definitions.
            See `get_all_extended_definitions()` to get the list of definitions with plugin
            extensions applied.

        Returns:
            List of AaC definitions
        """
        return copy.deepcopy(
            self.core_aac_spec_models
            | self.plugin_defined_models
            | self.validation_target_models
            | self.plugin_defined_extensions
        )

    def _apply_extension_to_model(self, model, extension):
        def add_values_to_model(model, extension_type, items, required=None):
            ext_type = f"{extension_type}Ext"

            model[extension_type][items] += extension[ext_type]["add"]

            if "required" in extension[ext_type]:
                model[extension_type][required] += extension[ext_type]["required"]

        if _is_enum_ext(extension):
            return add_values_to_model(model, "enum", "values")
        return add_values_to_model(model, "data", "fields", required="required")
