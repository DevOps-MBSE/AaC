---
layout: default
title: Modeling Data Structure Inheritance
parent: Developer's Guide to AaC
---

# Modeling Data Structure Inheritance
Architecture-as-Code allows users to model data structure inheritance in `schema` definitions, the definition type used to model data structures in AaC. Inheritance modeling is officially supported in AaC [version 0.1.4](https://github.com/DevOps-MBSE/AaC/releases/tag/v0.1.4) and above; users wanting to model data structure inheritance in earlier versions are able to do so with some extra work, see [Modeling Inheritance in 0.1.3 or Earlier Versions](#modeling-inheritance-in-013-or-earlier-versions).

# Modeling Inheritance in Current Versions
Version `0.1.4` of AaC introduced changes to support inheritance for `schema` definitions. The inheritance mechanism applies transitive attributes from the `fields` and `validation` fields from the parent definition(s). These attributes are applied to child definitions (sub-class definitions) automatically when ingested into a `LanguageContext`; this means that developers using AaC version `0.1.4` or above automatically have their inherited definitions' transitive attributes applied -- thus developers do not need to do any sort of lookup or resolving of inherited, transitive attributes.

## Supporting Structure Changes
The first change was to add an additional field to the `schema` definition named `inherits` that references other definition names:
```yaml
schema:
  name: schema
  fields:
    - name: name
      type: string
      description: |
        The name of the schema definition.
    - name: inherits              # <-- New Inherits Field
      type: DefinitionReference[] # <-- New DefinitionReference Structure
      description: |
        A list of Schema definition names that this definition inherits from.
    - name: fields
      type: Field[]
      description: |
        A list of fields that make up the definition.
    - name: validation
      type: ValidationReference[]
      description: |
        References and additional arguments for validations to apply to the definition.
  validation:
    - name: Root key is defined
    - name: Required fields are present
      arguments:
        - name
        - fields
    - name: Unique definition names
```

New Definition Reference Structure to link to other definitions:
```yaml
schema:
  name: DefinitionReference
  fields:
    - name: name
      type: string
  validation:
    - name: Type references exist
      arguments:
        - name
```
Example data structure with inheritance from `python/model/flow/DataA.yaml`:
```yaml
import:
  files:
    - ./DataMessage.yaml
---
schema:
  inherits:
    - DataMessage
  name: DataA
  fields:
  - name: request
    type: string
```

## Accessing Inherited Attributes
Inherited attributes are automatically applied to the child definition (sub-class definition), and can be accessed simply by accessing the child definitions' fields. In the above example where we reference `DataA` in `python/model/flow/DataA.yaml`, we can see that we'll inherit three fields (`source`, `destination`, and `content-length`) and no validations. So, despite `DataA` only declaring a single field, `request`, we'll find that the definition of `DataA` in the active context has inherited the three previously-mentioned fields:
```
Definition(
    uid=UUID('...'),
    name='DataA',
     content='...',
     source=AaCFile(...),
     lexemes=[...],
     structure={
        'schema': {
            'inherits': ['DataMessage'],
            'name': 'DataA',
            'fields': [
                {'name': 'request', 'type': 'string'},
                {'name': 'source', 'type': 'string'},      # <-- Inherited Field
                {'name': 'destination', 'type': 'string'}, # <-- Inherited Field
                {'name': 'content-length', 'type': 'int'}, # <-- Inherited Field
            ]
        }
    }
)
```

## Looking up Inherited Definitions
If you're interested in obtaining the definitions that are inherited by another definition, you can easily access the list of inherited definitions by accessing the `inherits` field, which returns a list of strings (definition names).
```python
active_context = get_active_context()
data_a_definition = get_active_context().get_definition_by_name("DataA")
inherited_definition_names = data_a_definition.get_inherits() # returns ['DataMessage']

# This loop will iterate over all of the parent definitions, if they're in the active context.
for definition_name in inherited_definition_names:
    parent_definition = get_active_context().get_definition_by_name(definition_name)
```

# Modeling Inheritance in 0.1.3 or Earlier Versions
While inheritance is not explicitly supported in version `0.1.3`, motivated users can recreate the mechanisms for their plugins.

## Recreate the Schema Changes
The first step will be alter the `schema` definition to support inheritance as mentioned in the [supporting changes](#modeling-inheritance-in-013-or-earlier-versions) section above.

Create the new `DefinitionReference` definition:
```yaml
schema:
  name: DefinitionReference
  fields:
    - name: name
      type: string
  validation:
    - name: Type references exist
      arguments:
        - name
```

Extend the schema structure to include the new `inherits` field:
```yaml
ext:
   name: SchemaInheritanceExtension
   type: schema
   schemaExt:
      add:
        - name: inherits
          type: DefinitionReference[]
```

## Accessing the Inherited Fields
Because `0.1.3` and earlier versions don't automatically apply inherited fields or validations, you will have to manually look them up. Start by getting the list of inherited definition names, look them up in the context, then extract the fields and validations from the parent definitions.

```python
active_context = get_active_context()
data_a_definition = get_active_context().get_definition_by_name("DataA")
inherited_definition_names = data_a_definition.get_top_level_fields().get("inherits") or []
# above line returns {'inherits': ['DataMessage'], 'name': 'DataA', 'fields': [{'name': 'request', 'type': 'string'}]}
#   or defaults to any empty list if the entry or `inherits` field is None.

# This loop will iterate over all of the parent definitions, if they're in the active context.
for definition_name in inherited_definition_names:
    parent_definition = get_active_context().get_definition_by_name(definition_name)
    inherited_fields = parent_definition.get_top_level_fields().get("fields") or [] # We access 'fields' again because this is a schema definition
    inherited_validation = parent_definition.get_top_level_fields().get("validation") or []
```
