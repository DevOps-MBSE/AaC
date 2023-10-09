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

AAC_LANG_FILE_NAME = "../../aac.aac"

class LanguageContext(object):
  """
    A singleton class that holds the current state of the AaC language.
  """

  def __new__(cls):
    if not hasattr(cls, 'context_instance'):
      cls.context_instance = super(LanguageContext, cls).__new__(cls)
      cls.context_instance.definitions = set()
      cls.context_instance.fully_qualified_name_to_definition: dict[str, Definition] = {}
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
      self.context_instance.fully_qualified_name_to_definition[f"{definition.package}.{definition.name}"] = definition

    return result   
        
  def get_definitions(self) -> list[Definition]:
    return list(self.context_instance.fully_qualified_name_to_definition.values())
    # return list(self.context_instance.definitions)
  
  # TODO:  it's possible there could be multiple definitions with the same name, but different packages
  # so need to clean this up
  def get_definition_by_name(self, name: str) -> Optional[Definition]:
    for definition in self.get_definitions():
      if definition.name == name:
        return definition
    return None
  
  def get_definitions_by_root(self, root_key: str) -> list[Definition]:
    result = []
    for definition in self.get_definitions():
      if definition.get_root_key() == root_key:
        result.append(definition)
    return result
  
  def get_definition_for_root_key(self, root_key: str) -> Definition:
    for definition in self.get_definitions():
      if definition.get_root_key() == root_key:
        return definition
    raise LanguageError(f"Could not find definition for root key: {root_key}")
  
  def get_defining_schema_for_root(self, root_key: str) -> Definition:
    for definition in self.get_definitions():
      if definition.get_root_key() == "schema":
        if definition.instance.root == root_key:
          return definition
    raise LanguageError(f"Could not find defining schema for root key: {root_key}")
  

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
    
  def is_extension_of(self, check_me: Definition, package: str, name: str) -> bool:
    # TODO: figure out if I need this or not
    return False

  def _recurse_type_inheritance(self, check_me: Definition) -> list[Definition]:
    result = []
    if "extends" in list(vars(check_me.instance).keys()):
      for extension in check_me.instance.extends:
        ext_package = extension.package
        ext_name = extension.name
        child_definition = self.context_instance.fully_qualified_name_to_definition[f"{ext_package}.{ext_name}"]
        result.append(child_definition)
        result.extend(self._recurse_type_inheritance(child_definition))
    return result

  def get_definitions_of_type(self, package: str, name: str) -> list[Definition]:
    result = []
    # first make sure we can find the definition that defines the type
    if f"{package}.{name}" not in self.context_instance.fully_qualified_name_to_definition:
      raise LanguageError(f"Could not find definition for {package}.{name}")
    # now get all the definitions that extend from the definition
    definition = self.context_instance.fully_qualified_name_to_definition[f"{package}.{name}"]
    result.append(definition)
    # loop through all definitions and see fi the type we care about is in it's inheritance tree
    for item in self.get_definitions():
      inheritance_types = self._recurse_type_inheritance(item)
      if f"{package}.{name}" in [f"{definition.package}.{definition.name}" for definition in inheritance_types]:
        result.append(item)
    return result
  
  def _traverse_field_chain(self, structure_list: list, field_chain: list[str]) -> list:
    current_structures = structure_list
    # print(f"DEBUG: !!!!!_traverse_field_chain!!!!! current_structures: searching for field_chain {field_chain}")
    search_depth = len(field_chain)
    current_depth = 0
    values_found = []
    for field_name in field_chain:
      next_structures = []
      # print(f"DEBUG: looking for field_name {field_name}")
      for structure in current_structures:
        # print(f"DEBUG: current_structure: {structure}")
        if field_name in structure:
          if isinstance(structure[field_name], list):
            # print(f"DEBUG: found field_name: {field_name} with list value {structure[field_name]}")
            if current_depth == search_depth - 1:
              values_found.extend(structure[field_name])
            else:
              next_structures.extend(structure[field_name])
          else:
            # print(f"DEBUG: found field_name: {field_name} with value {structure[field_name]}")
            if current_depth == search_depth - 1: # This just means we're at the end of the field chain and should pull the value
              # print(f"DEBUG: found field_name: {field_name} at search depth: {search_depth}")
              values_found.append(structure[field_name])
            else:
              # print(f"DEBUG: found field_name: {field_name} at search depth: {search_depth} but not at search depth.\nExtending search with {structure.get(field_name, [])}")
              next_structures.append(structure.get(field_name, []))
      current_structures = next_structures
      current_depth += 1
    # print(f"DEBUG: found values {values_found}")
    # raise LanguageError("DEBUG: stopping")
    return values_found

  def get_values_by_field_chain(self, search_term: str) -> list:
    result: list = []
    root_key = search_term.split(".")[0]
    candidate_values = self.get_definitions_by_root(root_key)
    result = self._traverse_field_chain([definition.structure for definition in candidate_values], search_term.split("."))
    return result
  