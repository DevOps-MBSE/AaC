import types
from typing import Any, Optional
from importlib import import_module
from copy import deepcopy
from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand
from aac.execute.aac_execution_result import LanguageError
from aac.execute.plugin_manager import get_plugin_manager
from aac.execute.plugin_runner import PluginRunner
from aac.io.parser._parse_source import parse
from aac.context.definition import Definition

AAC_LANG_FILE_NAME = "../lang/aac.aac"

class LanguageContext(object):
  """
    A singleton class that holds the current state of the AaC language.
  """

  def __new__(cls):
    if not hasattr(cls, 'context_instance'):
      cls.context_instance = super(LanguageContext, cls).__new__(cls)
      cls.context_instance.definitions = set()
      cls.context_instance.schema_name_to_module: dict[str, Any] = {}
      cls.context_instance.plugin_runners = {}

      # load and initialize the AaC language
      aac_lang_path = join(dirname(__file__), AAC_LANG_FILE_NAME)
      cls.context_instance.parse_and_load(aac_lang_path)

      # load plugins
      get_plugin_manager().hook.register_plugin()
      
    return cls.context_instance
  
  def parse_and_load(self, arg: str) -> list[Definition]:
    parsed_definitions = parse(arg)

    def get_python_module_name(name: str) -> str:
        return name.replace(" ", "_").replace("-", "_").lower()

    # TODO: handle the type error that occurs when bad data is found

    # schema_defs_by_name = {}
    schema_defs_by_root = {}
    for definition in self.get_definitions():
      if definition.get_root_key() == "schema":
        if definition.instance.root:
          schema_defs_by_root[definition.instance.root] = definition


    # we need to load all the schemas first so we have access to the defined types
    for definition in parsed_definitions:
      if "schema" in definition.structure:
        schema = definition.structure["schema"]
        if "name" in schema:
          name = schema["name"]
          if "package" in schema:
            package = schema["package"]
            python_name = get_python_module_name(name)
            if name not in self.context_instance.schema_name_to_module:
              module_name = f"{package}.{python_name}"
              module = import_module(module_name)
              # loaded_packages.add(package)
              self.context_instance.schema_name_to_module[name] = module
          # schema_defs_by_name[name] = definition
          if "root" in schema:
            root = schema["root"]
            schema_defs_by_root[root] = definition

    result: list[Definition] = []
    for definition in parsed_definitions:
      # figure out the python type for the definition
      root_key = definition.get_root_key()
      if root_key not in schema_defs_by_root:
        raise LanguageError(f"Could not find schema that defines root: {root_key}")
      defining_schema = schema_defs_by_root[root_key]
      if not defining_schema:
        raise LanguageError(f"Could not find schema for root: {root_key}")
      defining_schema_name = defining_schema.name
      if defining_schema_name not in self.context_instance.schema_name_to_module:
        raise LanguageError(f"Could not find module name: {defining_schema_name} in {list(self.context_instance.schema_name_to_module.keys())}")
      # get the structure below the root key
      structure = definition.structure[root_key]
      name = definition.name
      # create and register the instance
      class_obj = getattr(self.context_instance.schema_name_to_module[defining_schema_name], defining_schema_name)
      instance = None
      try:
        instance = class_obj.from_dict(deepcopy(structure))
      except TypeError as e:
        raise LanguageError(f"{e}\nCould not create instance of {defining_schema_name} with name {name} from structure: {structure}")
    
      definition.instance = instance
      result.append(definition)
      self.context_instance.definitions.add(definition)

    return result   
        
  def get_definitions(self) -> list[Definition]:
    return list(self.context_instance.definitions)
  
  def get_definition_by_name(self, name: str) -> Optional[Definition]:
    for definition in self.context_instance.definitions:
      if definition.name == name:
        return definition
    return None
  
  def get_definitions_by_root(self, root_key: str) -> list[Definition]:
    result = []
    for definition in self.context_instance.definitions:
      if definition.get_root_key() == root_key:
        result.append(definition)
    return result
  

  def register_plugin_runner(self, runner: PluginRunner) -> None:

    if runner.get_plugin_name() not in self.context_instance.plugin_runners:
      self.context_instance.plugin_runners[runner.get_plugin_name()] = runner
    else:
      print(f"Plugin {runner.get_plugin_name()} already registered.")

  def get_plugin_runners(self) -> list[PluginRunner]:
    return list(self.context_instance.plugin_runners.values())
  
  def get_primitives(self) -> list[Definition]:
    return self.get_definitions_by_root("primitive")
  
  def get_python_type_from_primitive(self, primitive_name: str) -> str:
    primitive = self.get_definition_by_name(primitive_name)
    if primitive:
      return primitive.instance.python_type
    else:
      raise LanguageError(f"Could not find primitive: {primitive_name}")
  