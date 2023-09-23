import types
from typing import Any
from importlib import import_module
from os.path import join, dirname
from aac.cli.aac_command import AacCommand
from aac.cli.aac_execution_result import LanguageError
from aac.io.parser._parse_source import parse
from aac.context.definition import Definition

AAC_LANG_FILE_NAME = "../lang/aac.aac"

class LanguageContext(object):

  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.context_instance = super(LanguageContext, cls).__new__(cls)
      cls.context_instance.definitions = set()
      cls.context_instance.instances_by_schema_name = {}
      aac_lang_path = join(dirname(__file__), AAC_LANG_FILE_NAME)
      cls.context_instance.parse_and_load(aac_lang_path)
    return cls.context_instance
  
  def parse_and_load(self, arg: str) -> None:
    parsed_definitions = parse(arg)
    self.register_definitions(parsed_definitions)

    def get_python_module_name(name: str) -> str:
        return name.replace(" ", "_").replace("-", "_").lower()

    schema_name_to_module: dict[str, Any] = {}
    schema_defs_by_name = {}
    schema_defs_by_root = {}

    # we need to load all the schemas first so we have access to the defined types
    for definition in parsed_definitions:
      if "schema" in definition.structure:
        schema = definition.structure["schema"]
        if "name" in schema:
          name = schema["name"]
          if "package" in schema:
            package = schema["package"]
            python_name = get_python_module_name(name)
            if name not in schema_name_to_module:
              module_name = f"{package}.{python_name}"
              module = import_module(module_name)
              # loaded_packages.add(package)
              schema_name_to_module[name] = module
          schema_defs_by_name[name] = definition
          if "root" in schema:
            root = schema["root"]
            schema_defs_by_root[root] = definition

    for definition in parsed_definitions:
      # figure out the python type for the definition
      root_key = definition.get_root_key()
      if root_key not in schema_defs_by_root:
        raise LanguageError(f"Could not find schema that defines root: {root_key}")
      defining_schema = schema_defs_by_root[root_key]
      if not defining_schema:
        raise LanguageError(f"Could not find schema for root: {root_key}")
      defining_schema_name = defining_schema.name
      if defining_schema_name not in schema_name_to_module:
        raise LanguageError(f"Could not find module name: {defining_schema_name} in {list(schema_name_to_module.keys())}")
      # get the structure below the root key
      structure = definition.structure[root_key]
      name = definition.name
      # create and register the instance
      print(f"DEBUG: creating instance of {defining_schema_name} for name {name} with {structure['name']}")
      class_obj = getattr(schema_name_to_module[defining_schema_name], defining_schema_name)
      print(f"DEBUG: getattr({schema_name_to_module[defining_schema_name]}, {defining_schema_name}) = class_obj: {class_obj}")
      instance = class_obj(structure)
      print(f"DEBUG: instance: {instance}")
      self.register_instance(instance)       
        
  
  def get_plugin_commands(self) -> list[AacCommand]:
    plugin_commands = []
    if self.context_instance.instances_by_schema_name:
      print(f"DEBUG: self.context_instance.instances_by_schema_name keys: {list(self.context_instance.instances_by_schema_name.keys())}")
      if "Plugin" in self.context_instance.instances_by_schema_name:
        plugins = self.context_instance.instances_by_schema_name["Plugin"]
        for plugin in plugins:
          if hasattr(plugin, "commands"):
            plugin_commands.extend(plugin.commands)
    return plugin_commands
  
  def register_instance(self, instance):
    if instance:
      print(f"DEBUG: registering instance: {instance}")
      class_name = instance.__class__.__name__
      if class_name not in self.context_instance.instances_by_schema_name:
        instance_list = []
        self.context_instance.instances_by_schema_name[class_name] = instance_list
      self.context_instance.instances_by_schema_name[class_name].append(instance)

  def register_instances(self, instances: list[Any]):
    if instances:
      for instance in instances:
        self.register_instance(instance)

  def register_definition(self, definition: Definition):
    if definition:
      self.context_instance.definitions.add(definition)

  def register_definitions(self, definitions: list[Definition]):
    if definitions:
      for definition in definitions:
        self.register_definition(definition)
