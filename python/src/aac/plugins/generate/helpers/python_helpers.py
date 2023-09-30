from aac.context.language_context import LanguageContext
from aac import __version__

# build out jinja2 utility functions
def get_python_name(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()

def get_python_primitive(aac_primitive_name: str) -> str:
    context = LanguageContext()
    aac_primitives = context.get_primitives()
    for aac_primitive in aac_primitives:
        if aac_primitive_name == aac_primitive.name:
            return aac_primitive.instance.python_type
    return "None"

def get_package_from_plugin(plugin_name: str) -> str:
    context = LanguageContext()
    plugin_runners = context.get_plugin_runners()
    for runner in plugin_runners:
        if plugin_name == runner.plugin_definition.name:
            return runner.plugin_definition.instance.package
    return f"aac.plugins.{get_python_name(plugin_name)}"

def get_path_from_package(package: str) -> str:
    return package.replace(".", "/")

def aac_version() -> str:
    return __version__