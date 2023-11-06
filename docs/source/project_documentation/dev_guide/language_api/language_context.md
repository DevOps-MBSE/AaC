---
layout: default
title: AaC Language Context
parent: Language API
nav_order: 3
has_children: false
---
# Using the AaC Language Context

Starting with AaC version `0.4.0`, the `LanguageContext` is central to the AaC developer's experience.  It provides one place to navigate all the definitions of your AaC model, starting with obtaining your model.

## Getting a Language Context

The AaC `LanguageContext` is implemented as a singleton and can be obtained by creating an instance.

```python
context = LanguageContext()
```

Because `LanguageContext` is a singleton, you will always receive the same content every time you create the instance.

## Parse and Load Definitions

The first thing you'll probably need to do if you're creating an AaC plugin is parsing and loading an AaC file.  The `LanguageContext` provides you with a simple way to do this.

```python
context = LanguageContext()
definitions = context.parse_and_load(my_aac_file)
```

This parses your content, populates the instance field in the resulting definitions, and loads these definitions into the `LanguageContext`.  The returned value is all the definitions that were parsed and loaded from the file provided.  

## Remove Definitions

There may be instances where you want to temporarily load some content but need to remove it.  This is a common when you're creating unit tests because you don't want some test data to be maintained in the `LanguageContext` singleton across unit tests.

```python
context = LanguageContext()
definitions = context.parse_and_load(my_test_data)
for definition in definitions:
    # perform some unit test logic
    self.fail(len(definition.name) > 16, "Definition name is too long.")
    context.remove(definition)
```

## AaC Core Language

The `LanguageContext` contains all definitions, including the AaC language definitions.  AaC is self-defining, so everything is present.  The LanguageContext provides some convenience functions for accessing AaC core language content.

- `get_aac_core_file_path`: Returns the location of the aac language definition file.
- `get_aac_core_as_yaml`:  Returns the YAML content of the aac language definition file.
- `get_aac_core_definitions`:  Returns the list of `Definition` items resulting from parseing and loading the aac language definition file.

## Finding Definitions

The `LanguageContext` contains all definitions and provides you a handful of ways to find loaded definitions.

- `get_definitions`: Returns a list of all loaded definitions.
- `get_definitions_by_name`: Searches and returns definitions with a specified name.
- `get_definitions_by_root`: Searches and returns definitions with a specified root.
- `get_definitions_of_type`: Searches and returns definitions with a specified type.  This works similarly to get_definitions_by_root, but uses the type name and handles inheritance.

## AaC Primitives

AaC defines primitives using the `primitive` root.  Primitives are valid field types in schemas and it can be useful to know what primitives are available within AaC.  To get a list of known primitives you call the `get_primitives` function.  In AaC, you can define any primitive you'd like, but it must have a corresponding python type for use in plugins and constraints. If you need quick access to the underlying python type for a primitive you call the `get_python_type_from_primitive` function.

## LanguageContext Convenience Functions

Since the `LanguageContext` serves as the "central hub" for everything, there are a handful of convenience functions included.  Here are a few examples.

- The LanguageContext keeps a list of registered AaC plugins which you can access using the `get_plugin_runners` function.
- If you need to know if a definition inherits from another definitions you can use the `LanguageContext` function `is_extension_of`.
- If you need a listing of all values for a particular data reference you can use the `LanguageContext` function `get_values_by_field_chain` where field_chain is a dot notation representative of fields in your definition.
- If you need to create a python instance of an AaC enumeration (i.e. `enum`) you can use the `LanguageContext` function `create_aac_enum`.  Under the covers, AaC is dynamically creating a python `Enum`, but since we're not generating persistent code you can't just create your own instance.  This function gives you the ability to create instances based on the dynamically created python `Enum`.  This is particularly useful for unit testing.
- If you need to create a python instance of an AaC schema class (i.e. `schema`) you can use the `LanguageContext` function `create_aac_object`.  Under the covers, AaC is dynamically creating a python class for each `schema`, but since we're not generating persistent code you can't just create your own instance.  This function gives you the ability to create instances based on the dynamically created python class.  This is particularly useful for unit testing.