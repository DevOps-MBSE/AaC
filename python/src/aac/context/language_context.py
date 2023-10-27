import types
from typing import Any, Optional, Type
from enum import Enum, auto
from os import linesep
from os.path import join, dirname, sep
from aac.execute.plugin_runner import AacCommand
from aac.context.language_error import LanguageError
from aac.execute.plugin_manager import get_plugin_manager
from aac.execute.plugin_runner import PluginRunner
from aac.in_out.parser._parse_source import parse
from aac.context.definition import Definition
from aac.context.util import get_python_module_name, get_python_class_name

AAC_LANG_FILE_NAME = "../../aac.aac"
AAC_LANG_FILE_PATH = join(dirname(__file__), AAC_LANG_FILE_NAME)

class LanguageContext(object):
  """
    A singleton class that holds the current state of the AaC language.
  """

  def __new__(cls):
    if not hasattr(cls, 'context_instance'):
      cls.context_instance = super(LanguageContext, cls).__new__(cls)
      cls.context_instance.definitions = set()
      cls.context_instance.fully_qualified_name_to_definition: dict[str, Definition] = {}
      cls.context_instance.fully_qualified_name_to_class: dict[str, Any] = {}
      cls.context_instance.plugin_runners = {}

      # load and initialize the AaC language
      cls.context_instance.parse_and_load(AAC_LANG_FILE_PATH)

      # load plugins
      get_plugin_manager().hook.register_plugin()
      
    return cls.context_instance
  
  def get_aac_core_file_path(self) -> str:
    return AAC_LANG_FILE_PATH
  
  def get_aac_core_as_yaml(self) -> str:
    with open(AAC_LANG_FILE_PATH) as aac_file:
        return aac_file.read()
  
  def get_aac_core_definitions(self) -> list[Definition]:
    return self.parse_and_load(AAC_LANG_FILE_PATH)
  
  def _get_aac_generated_class(self, name: str) -> Type:
    definitions = self.get_definitions_by_name(name)
    if len(definitions) != 1:
      raise LanguageError(f"_get_aac_generated_class unable to identify unique definition for name '{name}'.  Found: {[definition.name for definition in definitions]}")
    
    aac_class = self.context_instance.fully_qualified_name_to_class[definitions[0].get_fully_qualified_name()]
    if not aac_class:
      raise LanguageError(f"_get_aac_generated_class unable to identify generated class for name '{name}' with fully_qualified_name '{definitions[0].get_fully_qualified_name()}'")
    
    return aac_class
  
  def is_aac_instance(self, obj: Any, name: str):
    
    return isinstance(obj, self._get_aac_generated_class(name))
  
  def create_aac_object(self, aac_type_name: str, attributes: dict) -> Any:
    definitions = self.get_definitions_by_name(aac_type_name)
    if len(definitions) != 1:
      raise LanguageError(f"Unable to identify unique definition for '{aac_type_name}'.  Found {[definition.name for definition in definitions]}")
    aac_class = self._get_aac_generated_class(aac_type_name)
    result = aac_class()
    field_names = [field.name for field in definitions[0].instance.fields]
    for attribute_name, attribute_value in attributes.items():
      if attribute_name not in field_names:
        raise LanguageError(f"Found undefined field name '{attribute_name}'")
      setattr(result, attribute_name, attribute_value)
    return result
  
  def create_aac_enum(self, aac_enum_name: str, value: str) -> Any:
    definitions = self.get_definitions_by_name(aac_enum_name)
    if len(definitions) != 1:
      raise LanguageError(f"Unable to identify unique definition for '{aac_enum_name}'.  Found {[definition.name for definition in definitions]}")
    aac_class = self._get_aac_generated_class(aac_enum_name)
    try:
      return getattr(aac_class, value)
    except ValueError:
      raise LanguageError(f"{value} is not a valid value for enum {aac_enum_name}")
  
  def parse_and_load(self, arg: str) -> list[Definition]:
    parsed_definitions = parse(arg)

    return self.load_definitions(parsed_definitions)
  
  def load_definitions(self, parsed_definitions: list[Definition]) -> list[Definition]:
    """
    Loads the given definitions into the context and populates the instance with a python object.
    """

    # Maintainer note:  Yes, this function is a bit of a monster...sorry about that.
    # I wanted to keep all this stuff together because if it all works out this should be the 
    # only place where we have to deal with navigating the structure of the definitions and
    # not using the python objects.  In order for this to work, any changes in here should
    # avoid the use of he definition instance...other than actually creating it.

    primitive_name_to_py_type = {definition.name : definition.structure["primitive"]["python_type"] for definition in parsed_definitions + self.get_definitions() if definition.get_root_key() == "primitive"}
    fully_qualified_name_to_definition = {}

    def find_definitions_by_name(name: str) -> list[Definition]:
      result = []
      for definition in self.get_definitions():
        if definition.name == name:
          result.append(definition)
      # if we didn't find any definitions in the context, check the parsed definitions
      if len(result) == 0:
        for definition in parsed_definitions:
          if definition.name == name:
            result.append(definition)
      return result
    
    def get_inheritance_parents(definition: Definition) -> list[Type]:
      """
      Looks up the inheritance parent classes for the given definition and returns them as a list of python classes.
      """
      inheritance_parents = []

      if "extends" in definition.structure[definition.get_root_key()]:
        for parent in definition.structure[definition.get_root_key()]["extends"]:
          # I need to find the definition referenced by the extends
          parent_package = parent["package"]
          parent_name = parent["name"]
          parent_fully_qualified_name = parent_fully_qualified_name = f"{get_python_module_name(parent_package)}.{get_python_class_name(parent_name)}"
          if parent_fully_qualified_name in self.context_instance.fully_qualified_name_to_class:
            inheritance_parents.append(self.context_instance.fully_qualified_name_to_class[parent_fully_qualified_name])
          else:
            # there is a chance that processing order just means we haven't gotten to the parent yet
            parent_definition = None
            if parent_fully_qualified_name in fully_qualified_name_to_definition:
              parent_definition = fully_qualified_name_to_definition[parent_fully_qualified_name]

            if not parent_definition:
              raise LanguageError(f"Cannot find parent definition {parent_fully_qualified_name} for {definition.name}")
            
            if parent_definition.get_root_key() == "schema":
              create_schema_class(parent_definition)
              inheritance_parents.append(self.context_instance.fully_qualified_name_to_class[parent_fully_qualified_name])
            elif parent_definition.get_root_key() == "enum":
              create_enum_class(parent_definition)
              inheritance_parents.append(self.context_instance.fully_qualified_name_to_class[parent_fully_qualified_name])
            else:
              # TODO:  does this really need to be an error?  I can't think of an alternative right now, and it's generally consistent with coding language conventions.
              # Would it even be possible for an AaC developer to create some new thing that doesn't use "schema" or "enum" to define base non-primitive types?
              raise LanguageError(f"AaC extension is only supported for Schema and Enum.  Unable to create parent class with AaC root: {parent_definition.get_root_key()}")
            
      return inheritance_parents
    
    def create_enum_class(enum_definition: Definition) -> Type:

      # TODO:  since we're not generaing code any more, can we go back to 'enum' instead of 'enum'?
      if not enum_definition.get_root_key() == "enum":
        raise LanguageError(f"Definition {enum_definition.name} is not an enum")
      
      fully_qualified_name = enum_definition.get_fully_qualified_name()
      if fully_qualified_name in self.context_instance.fully_qualified_name_to_class:
        # we've already created the class, so nothing to do here
        return self.context_instance.fully_qualified_name_to_class[fully_qualified_name]

      # Note:  trying to allow extension with Enums fails, so I just removed it
      #        but we can revisit and try to find a solution in the future if needed
      
      values = {}
      if "values" in enum_definition.structure["enum"]:
        for value in enum_definition.structure["enum"]["values"]:
          values[value] = auto()
      # create the enum class
      instance_class = Enum(enum_definition.get_python_class_name(), values, module=enum_definition.get_python_module_name())
      self.context_instance.fully_qualified_name_to_class[fully_qualified_name] = instance_class
      return instance_class

    def create_schema_class(schema_definition: Definition) -> Type:
      instance_class = None

      fully_qualified_name = schema_definition.get_fully_qualified_name()
      if schema_definition.get_root_key() == "primitive":
        # this is a primitive, so there's no structure to create...just return the python type
        return eval(primitive_name_to_py_type[schema_definition.name])
      elif schema_definition.get_root_key() == "enum":
        # this is an enum, so create the enum class
        return create_enum_class(schema_definition)
      elif schema_definition.get_root_key() != "schema":
        raise LanguageError(f"Definition {schema_definition.name} is not a schema")
      
      if fully_qualified_name in self.context_instance.fully_qualified_name_to_class:
        # we've already created the class, so nothing to do here
        return self.context_instance.fully_qualified_name_to_class[fully_qualified_name]
      
      instance_class = None
      inheritance_parents = get_inheritance_parents(schema_definition)
      if len(inheritance_parents) == 0:
        instance_class = type(schema_definition.get_python_class_name(), tuple([object]), {"__module__": schema_definition.get_python_module_name()})
      else:
        parent_classes = inheritance_parents  # the following causes a method resolution order (MRO) error when creating the type: [object] + inheritance_parents
        instance_class = type(definition.get_python_class_name(), tuple(parent_classes), {"__module__": schema_definition.get_python_module_name()})

      # now add the fields to the class
      for field in schema_definition.structure["schema"]["fields"]:
        field_name = field["name"]
        field_type = field["type"]
        is_list = False

        clean_field_type = field_type
        if field_type.endswith("[]"):
          is_list = True
          clean_field_type = field_type[:-2]
        if "(" in clean_field_type:
          clean_field_type = clean_field_type[:clean_field_type.find("(")]

        # let's make sure the type of the field is known, or create it if it's not
        potential_definitions = find_definitions_by_name(clean_field_type)
        if len(potential_definitions) != 1:
          line = 0
          for lexeme in definition.lexemes:
            if lexeme.value == field_type:
              line = lexeme.location.line
              break
          if len(potential_definitions) == 0:
            raise LanguageError(sep.join([f"Could not find AaC definition for type {clean_field_type} while loading {schema_definition.name}", f"  File: {schema_definition.source.uri}  Line: {line}"]))
          else:
            raise LanguageError(sep.join([f"Discovered multipe AaC definitions for type {clean_field_type} while loading {schema_definition.name}.  You may need to add a package name to differentiate.", f"  File: {schema_definition.source.uri}  Line: {line}", f"  Found candidate definitions: {[definition.get_fully_qualified_name() for definition in potential_definitions]}"]))
        
        parsed_definition = potential_definitions[0] 
        
        create_schema_class(parsed_definition)

        # since python is dynamically typed, we really don't have to worry about setting a type when we create the field
        # we just need to make sure a reasonable default value is used, so for us that means an empty list or None
        # TODO:  see if there's ever a case where we may need a dict value       
        if is_list:
          setattr(instance_class, field_name, [])
        else:
          setattr(instance_class, field_name, None)
 
      # finally store the class in the context
      self.context_instance.fully_qualified_name_to_class[fully_qualified_name] = instance_class
      return instance_class
    
    def create_object_instance(type_class: Type, fields: dict) -> Any:
      result = type_class()
      for field_name, field_value in fields.items():
        setattr(result, field_name, field_value)
      return result
    
    def create_field_instance(field_name: str, field_type: str, is_required: bool, field_value: Any) -> Any:
      """
      Creates a instance of the given type and value.
      """
      is_list = False
      clean_field_type = field_type
      if field_type.endswith("[]"):
        is_list = True
        clean_field_type = field_type[:-2]
      if "(" in clean_field_type:
        clean_field_type = clean_field_type[:clean_field_type.find("(")]
        
      # now get the defining definition from the clean_field_type
      defining_definitions = find_definitions_by_name(clean_field_type)
      if not defining_definitions or len(defining_definitions) == 0:
        raise LanguageError(f"Could not find definition for '{clean_field_type}'.")
      elif len(defining_definitions) > 1:
        raise LanguageError(f"Found multiple definitions for '{clean_field_type}'.")
      defining_definition = defining_definitions[0]
      
      if defining_definition.get_root_key() == "primitive":
        # this is a primitive, so ensure the parsed value aligns with the type and return it
        python_type = defining_definition.structure["primitive"]["python_type"]
        if is_list:
          if not field_value:
            if is_required:
              raise LanguageError(f"Missing required field {field_name}.")
            field_value = []
          else:
            for item in field_value:
              if not isinstance(item, eval(python_type)):
                raise LanguageError(f"Invalid value for field '{field_name}'.  Expected type '{python_type}', but found '{type(item)}'")
        else:
          if not field_value:
            if is_required:
              raise LanguageError(f"Missing required field {field_name}.")
          else:
            if "Any" != python_type:
              if not isinstance(field_value, eval(python_type)):
                raise LanguageError(f"Invalid value for field '{field_name}'.  Expected type '{python_type}', but found '{type(field_value)}'")
        return field_value
      elif defining_definition.get_root_key() == "enum":
        # this is an enum, so ensure the parsed value aligns with the type and return it
        enum_class = self.context_instance.fully_qualified_name_to_class[defining_definition.get_fully_qualified_name()]
        if not enum_class:
          enum_class = create_enum_class(defining_definition)
        if is_list:
          result = []
          for item in field_value:
            if not isinstance(item, str):
              raise LanguageError(f"Invalid value for field '{field_name}'.  Expected type 'str', but found '{type(item)}'")
            try:
              result.append(getattr(enum_class, item))
            except ValueError:
              raise LanguageError(f"{item} is not a valid value for enum {defining_definition.name}")
          return result
        else:
          if not field_value:
            return None
          try:
            return self.create_aac_enum(defining_definition.get_fully_qualified_name(), field_value)
            # return getattr(enum_class, field_value)
          except ValueError:
            raise LanguageError(f"{field_value} is not a valid value for enum {defining_definition.name}")
      else:
        field_fully_qualified_name = defining_definition.get_fully_qualified_name()
        
        instance_class = self.context_instance.fully_qualified_name_to_class[field_fully_qualified_name]
        if not instance_class:
          if defining_definition.get_root_key() == "schema":
            instance_class = create_schema_class(defining_definition)
          else:
            raise LanguageError("figure out what to do here")
        instance = None
        if is_list:
          instance = []
          if not field_value:
            if is_required:
              raise LanguageError(f"Missing required field {field_name}")
          else:
            if not isinstance(field_value, list):
              if is_required:
                raise LanguageError(f"Invalid parsed value for field '{field_name}'.  Expected type 'list', but found '{type(field_value)}'.  Value = {field_value}")
              else:
                return instance
            for item in field_value:
              if not isinstance(item, dict):
                raise LanguageError(f"Invalid parsed value for field '{field_name}'.  Expected type 'dict', but found '{type(item)}'. Value = {item}")
              # go through the fields and create instances for each
              subfields = {}
              if "fields" not in defining_definition.structure["schema"]:
                raise LanguageError(f"Schema '{defining_definition.name}' does not contain any fields.")
              for subfield in defining_definition.structure["schema"]["fields"]:
                subfield_name = subfield["name"]
                subfield_type = subfield["type"]
                subfield_is_required = False
                if "is_required" in subfield:
                  subfield_is_required = subfield["is_required"]
                subfield_value = None
                if subfield_name in item:
                  subfield_value = item[subfield_name]
                else:
                  if "default_value" in subfield:
                    subfield_value = subfield["default_value"]
                subfields[subfield_name] = create_field_instance(subfield_name, subfield_type, subfield_is_required, subfield_value)
              instance.append(create_object_instance(instance_class, subfields))
        else:
          instance = None
          if not field_value:
            if is_required:
              raise LanguageError(f"Missing required field {field_name}")
            else:
              return instance
          if not isinstance(field_value, dict):
            # this is a complex type defined by a schema, with a field value so it should be a dict
            raise LanguageError(f"Invalid parsed value for field '{field_name}'.  Expected type 'dict', but found '{type(field_value)}'.  Value = {field_value}")
          
          subfields = {}
          if "fields" not in defining_definition.structure["schema"]:
            raise LanguageError(f"Schema '{defining_definition.name}' does not contain any fields.")
          for subfield in defining_definition.structure["schema"]["fields"]:
            subfield_name = subfield["name"]
            subfield_type = subfield["type"]
            subfield_is_required = False
            if "is_required" in subfield:
              subfield_is_required = subfield["is_required"]
            subfield_value = None
            if subfield_name in field_value:
              subfield_value = field_value[subfield_name]
            else:
              if "default_value" in subfield:
                subfield_value = subfield.default_value
            subfields[subfield_name] = create_field_instance(subfield_name, subfield_type, subfield_is_required, subfield_value)
          
          instance = create_object_instance(instance_class, subfields)

        return instance
    
    def create_definition_instance(definition: Definition) -> Any:
      """
      Populates the instance field of a given definition.
      """
      instance = None
      
      defining_definition = None
      for item in self.get_definitions() + parsed_definitions:
        if item.get_root_key() == "schema":
          if "root" in item.structure["schema"]:
            if definition.get_root_key() == item.structure["schema"]["root"]:
              defining_definition = item

      if not defining_definition:
        raise LanguageError(f"Could not find definition for {definition.name} with root {definition.get_root_key()}")
      
      if defining_definition.get_root_key() == "schema":
        # since schemas are how we define "all the things" the root key of the defining definition should be 'schema'
        create_schema_class(defining_definition)
      else:
        raise LanguageError(f"Definition for root key '{defining_definition.get_root_key()}' is not a Schema.")

      instance = create_field_instance("root", defining_definition.name, True, definition.structure[definition.get_root_key()])

      definition.instance = instance
      return instance

    # Start the load_definition function code here

    fully_qualified_name_to_definition = {definition.get_fully_qualified_name() : definition for definition in parsed_definitions + self.get_definitions() if "package" in definition.structure[definition.get_root_key()]}

    schema_defs_by_root = {}
    for definition in self.get_definitions():
      if definition.get_root_key() == "schema":
        if definition.instance.root:
          schema_defs_by_root[definition.instance.root] = definition

    result: list[Definition] = []
    for definition in parsed_definitions:
      # create and register the instance
      create_definition_instance(definition)
      result.append(definition)
      self.context_instance.definitions.add(definition)
      self.context_instance.fully_qualified_name_to_definition[f"{definition.package}.{definition.name}"] = definition

    return result

  def remove_definitions(self, definitions: list[Definition]) -> None:
    for definition in definitions:
      self.context_instance.definitions.remove(definition)
      del self.context_instance.fully_qualified_name_to_definition[f"{definition.package}.{definition.name}"]  
        
  def get_definitions(self) -> list[Definition]:
    return list(self.context_instance.fully_qualified_name_to_definition.values())
    # return list(self.context_instance.definitions)
  
  # TODO:  it's possible there could be multiple definitions with the same name, but different packages
  # so need to clean this up
  # def get_definition_by_name(self, name: str) -> Optional[Definition]:
  #   for definition in self.get_definitions():
  #     if definition.name == name:
  #       return definition
  #   return None
  
  def get_definitions_by_name(self, name: str) -> list[Definition]:
    result = []
    search_name = name
    if "." not in name:
      search_name = f".{name}"
    for definition in self.get_definitions():
      if definition.get_fully_qualified_name().endswith(search_name):
        result.append(definition)
    return result
  
  def get_definitions_by_root(self, root_key: str) -> list[Definition]:
    result = []
    for definition in self.get_definitions():
      if definition.get_root_key() == root_key:
        result.append(definition)
    return result
  
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
    primitives = self.get_definitions_by_name(primitive_name)
    if len(primitives) != 1:
      raise LanguageError(f"Could not find unique primitive type: {primitive_name} - discovered {[primitive.name for primitive in primitives]}")
    return primitives[0].instance.python_type
    
  def is_extension_of(self, check_me: Definition, package: str, name: str) -> bool:
    definitions_of_type = self.get_definitions_of_type(package, name)
    return check_me in definitions_of_type

  def _recurse_type_inheritance(self, check_me: Definition) -> list[Definition]:
    result = []
    if "extends" in list(vars(check_me.instance).keys()):
      for extension in check_me.instance.extends:
        ext_package = extension.package
        ext_name = extension.name
        parent_definition = self.context_instance.fully_qualified_name_to_definition[f"{ext_package}.{ext_name}"]
        result.append(parent_definition)
        result.extend(self._recurse_type_inheritance(parent_definition))
    return result

  def get_definitions_of_type(self, package: str, name: str) -> list[Definition]:
    result = []
    # first make sure we can find the definition that defines the type
    if f"{package}.{name}" not in self.context_instance.fully_qualified_name_to_definition:
      raise LanguageError(f"Could not find definition for {package}.{name}")
    # now get all the definitions that extend from the definition
    definition = self.context_instance.fully_qualified_name_to_definition[f"{package}.{name}"]
    result.append(definition)
    # loop through all definitions and see if the type we care about is in it's inheritance tree
    for item in self.get_definitions():
      inheritance_types = self._recurse_type_inheritance(item)
      if f"{package}.{name}" in [f"{definition.package}.{definition.name}" for definition in inheritance_types]:
        result.append(item)
    return result
  
  def _traverse_field_chain(self, structure_list: list, field_chain: list[str]) -> list:
    current_structures = structure_list
    search_depth = len(field_chain)
    current_depth = 0
    values_found = []
    for field_name in field_chain:
      next_structures = []
      for structure in current_structures:
        if field_name in structure:
          if isinstance(structure[field_name], list):
            if current_depth == search_depth - 1:
              values_found.extend(structure[field_name])
            else:
              next_structures.extend(structure[field_name])
          else:
            if current_depth == search_depth - 1: # This just means we're at the end of the field chain and should pull the value
              values_found.append(structure[field_name])
            else:
              next_structures.append(structure.get(field_name, []))
      current_structures = next_structures
      current_depth += 1
      
    return values_found

  def get_values_by_field_chain(self, search_term: str) -> list:
    result: list = []
    root_key = search_term.split(".")[0]
    candidate_values = self.get_definitions_by_root(root_key)
    result = self._traverse_field_chain([definition.structure for definition in candidate_values], search_term.split("."))
    return result
  