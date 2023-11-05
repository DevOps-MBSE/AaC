"""Python helpers for the generate plugin that can be passed into Jinja2 and used in templates."""
from aac.context.language_context import LanguageContext
from aac import __version__
from typing import Any


# build out jinja2 utility functions
def get_python_name(name: str) -> str:
    """Returns the python name for an AaC name."""
    if name.startswith("--"):
        name = name[2:]
    return name.replace(" ", "_").replace("-", "_").lower()


def get_python_primitive(aac_primitive_name: str) -> str:
    """Returns the python primitive for an AaC primitive."""
    context = LanguageContext()
    aac_primitives = context.get_primitives()
    clean_name = aac_primitive_name
    if clean_name.endswith("[]"):
        clean_name = clean_name[:-2]
    if clean_name.find("(") > -1:
        clean_name = clean_name[: clean_name.find("(")]
    for aac_primitive in aac_primitives:
        if clean_name == aac_primitive.name:
            return aac_primitive.instance.python_type
    return "None"


def get_python_type(aac_type_name: str) -> str:
    """Returns the python type for an AaC type."""
    context = LanguageContext()
    if aac_type_name.endswith("[]"):
        aac_type_name = aac_type_name[:-2]
        return f"list[{get_python_type(aac_type_name)}]"
    elif aac_type_name in [primitive.name for primitive in context.get_primitives()]:
        return context.get_python_type_from_primitive(aac_type_name)
    else:
        return aac_type_name


def get_package_from_plugin(plugin_name: str) -> str:
    """Returns the package for an AaC plugin."""
    context = LanguageContext()
    plugin_runners = context.get_plugin_runners()
    for runner in plugin_runners:
        if plugin_name == runner.plugin_definition.name:
            return runner.plugin_definition.instance.package
    return f"aac.plugins.{get_python_name(plugin_name)}"


def get_package_from_aac_definition(item_name: str) -> str:
    """Returns the package for an AaC definition."""
    context = LanguageContext()
    definitions = context.get_definitions()
    for definition in definitions:
        if definition.name == item_name:
            return definition.instance.package
    return ""


def get_path_from_package(package: str) -> str:
    """Converts a package to a path."""
    return package.replace(".", "/")


def aac_version() -> str:
    """Returns the current version of AaC."""
    return __version__


def _generate_test_data_for_primitive(primitive_type: str) -> Any:
    if primitive_type == "str":
        return "test"
    elif primitive_type == "int":
        return 1
    elif primitive_type == "float":
        return 1.1
    elif primitive_type == "bool":
        return True
    elif primitive_type == "Any":
        return "{}"
    else:
        raise Exception(f"Unknown primitive type: {primitive_type}")


def schema_to_test_dict(name: str, omit_optional_fields: bool = False) -> dict:
    """Generate test data for a schema to a dictionary based on its fields."""
    context: LanguageContext = LanguageContext()
    schema_definitions = context.get_definitions_by_name(name)
    if len(schema_definitions) != 1:
        raise Exception(f"Could not find unique schema definition: {name}")
    schema_definition = schema_definitions[0]
    result: dict = {}

    # we need to avoid the case where a schema is defining an AaC type other than Schema
    if schema_definition.get_root_key() == "enum":
        # need to return a valid enum value
        for value in schema_definition.instance.values:
            return value

    for field in schema_definition.instance.fields:
        if omit_optional_fields and not field.is_required:
            continue

        clean_field_type = get_python_primitive(field.type)
        if clean_field_type == "None":
            # this is a schema type
            if field.type.endswith("[]"):
                # this is an array of schema types
                result[field.name] = [
                    schema_to_test_dict(field.type[:-2], omit_optional_fields),
                    schema_to_test_dict(field.type[:-2], omit_optional_fields),
                ]
            else:
                result[field.name] = schema_to_test_dict(
                    field.type, omit_optional_fields
                )
        else:
            # this is a primitive type
            if field.type.endswith("[]"):
                # this is an array of primitive types
                result[field.name] = [
                    _generate_test_data_for_primitive(clean_field_type),
                    _generate_test_data_for_primitive(clean_field_type),
                ]
            else:
                result[field.name] = _generate_test_data_for_primitive(clean_field_type)

    return result
