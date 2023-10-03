from aac.context.language_context import LanguageContext
from aac import __version__

# build out jinja2 utility functions
def get_python_name(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()

def get_python_primitive(aac_primitive_name: str) -> str:
    context = LanguageContext()
    aac_primitives = context.get_primitives()
    primitive_name = aac_primitive_name
    if aac_primitive_name.endswith("[]"):
        primitive_name = aac_primitive_name[:-2]
    if aac_primitive_name.startswith("reference("):
        primitive_name = "reference"
    for aac_primitive in aac_primitives:
        if primitive_name == aac_primitive.name:
            return aac_primitive.instance.python_type
    return "None"

def get_python_type(aac_type_name: str) -> str:
    context = LanguageContext()
    if aac_type_name.endswith("[]"):
        aac_type_name = aac_type_name[:-2]
        return f"list[{get_python_type(aac_type_name)}]"
    elif aac_type_name in [primitive.name for primitive in context.get_primitives()]:
        return context.get_python_type_from_primitive(aac_type_name)
    else:
        return aac_type_name

def get_package_from_plugin(plugin_name: str) -> str:
    context = LanguageContext()
    plugin_runners = context.get_plugin_runners()
    for runner in plugin_runners:
        if plugin_name == runner.plugin_definition.name:
            return runner.plugin_definition.instance.package
    return f"aac.plugins.{get_python_name(plugin_name)}"

def get_package_from_aac_definition(item_name: str) -> str:
    context = LanguageContext()
    definitions = context.get_definitions()
    for definition in definitions:
        if definition.name == item_name:
            return definition.instance.package
    return ""

def get_path_from_package(package: str) -> str:
    return package.replace(".", "/")

def aac_version() -> str:
    return __version__