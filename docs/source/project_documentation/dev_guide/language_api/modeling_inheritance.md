---
layout: default
title: Modeling Data Structure Inheritance
parent: Developer's Guide to AaC
---

# AaC Inheritance Capaility and Limitations

Version `0.4.0` changed how inheritance works in AaC.  AaC now provides a more "standard" inheritance construct within the `Schema` data declaration using the `extends` field.  By "standard", we mean you can extend your `Schema` in the same way you would extend a python class since AaC uses python under the hood.  In short, you can extend schemas using an object-oriented mindset.  That said, this only applies to `Schema`.  While it is technically possible to extend an `Enum` in python, AaC does not support `enum` extension.  This may be revisited in the future, but initial attempts to support Enum extension in the underlying python code generation did not work.  And of course, extending primitives is not a thing (but you can define new primitives).

# Modeling AaC Inheritance

Let's take a quick look at this how AaC supports `Schema` inheritance.

Example AaC Schema extension:
```yaml
schema:
  name: Person
  package: aac.example
  root: person
  fields:
    - name: name
      type: string
    - name: age
      type: int
---
schema:
  name: Employee
  package: aac.example
  root: employee
  extends:
    - name: Person
      package: aac.example
  fields:
    - name: id
      type: string
```

We've defined a generic person and extended that to an employee which adds the `id` field.  To use these in an AaC model we would do the following.

```yaml
person:
  name: Sally
  age: 36
---
employee:
  name: Ray
  age: 28
  id: S234110
```

# Inheritance Modifiers

Just as in most programming languages, the AaC language provides some basic modifiers to control what you can and can't do with inheritance.

- `abstract` - This allows you to declare your schema as an abstract type, meaning it cannot be "instantiated" directly in a declaration.  In AaC you can think of this as either being a root type or field in another `Schema`.
- `final` - This allows you to declare your schema as a final type, meaning it cannot be extended by another `Schema`.  In AaC this means you cannot include the final schema in another schema's extends field.

To use these inheritance modifiers you simply add them to the modifiers field of the schema.  Let's update the previous example to see how this works.

```yaml
schema:
  name: Person
  package: aac.example
  modifiers:
    - abstract
  fields:
    - name: name
      type: string
    - name: age
      type: int
---
schema:
  name: Employee
  package: aac.example
  modifiers:
    - final
  root: employee
  extends:
    - name: Person
      package: aac.example
  fields:
    - name: id
      type: string
```

We can no longer instantiate a Person because it is now `abstract`.  We would also be prevented from creating something like `SalaryEmployee` that would extend `Employee` because `Employee` has the `final` modifier.

## Using Inheritance

Now that we can define inheritance, how can we use it.  The intended use case is to allow polymorphism in your field declaration.  Let's look at another example to explain.

```yaml
schema:
  name: Person
  package: aac.example
  modifiers:
    - abstract
  fields:
    - name: name
      type: string
    - name: age
      type: int
---
schema:
  name: Employee
  package: aac.example
  modifiers:
    - final
  extends:
    - name: Person
      package: aac.example
  fields:
    - name: id
      type: string
schema:
  name: Contractor
  package: aac.example
  modifiers:
    - final
  extends:
    - name: Person
      package: aac.example
  fields:
    - name: contractor_id
      type: string
    - name: supplier
      type: string
---
schema:
  name: Team
  package: aac.example
  root: team
  fields:
    - name: name
      type: string
    - name: members
      type: typeref(aac.example.Person)
```

We no longer define individuals but teams, and that team includes members that can be made up of `Employee` or `Contractor`.

# Inheritance prior to AaC 0.4.0

## Modeling Data Structure Inheritance
Architecture-as-Code allows users to model data structure inheritance in `schema` definitions, the definition type used to model data structures in AaC. Inheritance modeling is officially supported in AaC [version 0.1.4](https://github.com/DevOps-MBSE/AaC/releases/tag/v0.1.4) and above; users wanting to model data structure inheritance in earlier versions are able to do so with some extra work, see [Modeling Inheritance in 0.1.3 or Earlier Versions](#modeling-inheritance-in-013-or-earlier-versions).

## Modeling Inheritance in Current Versions
Version `0.1.4` of AaC introduced changes to support inheritance for `schema` definitions. The inheritance mechanism applies transitive attributes from the `fields` and `validation` fields from the parent definition(s). These attributes are applied to child definitions (sub-class definitions) automatically when ingested into a `LanguageContext`; this means that developers using AaC version `0.1.4` or above automatically have their inherited definitions' transitive attributes applied -- thus developers do not need to do any sort of lookup or resolving of inherited, transitive attributes.

### Supporting Structure Changes
The first change was to add an additional field to the `schema` definition named `inherits` that references other definition names:

```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/spec/spec.yaml
    :language: yaml
    :lines: 266-311
    :emphasize-lines: 22-25
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

### Accessing Inherited Attributes
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

### Looking up Inherited Definitions
If you're interested in obtaining the definitions that are inherited by another definition, you can easily access the list of inherited definitions by accessing the `inherits` field, which returns a list of strings (definition names).
```python
active_context = get_active_context()
data_a_definition = get_active_context().get_definition_by_name("DataA")
inherited_definition_names = data_a_definition.get_inherits() # returns ['DataMessage']

# This loop will iterate over all of the parent definitions, if they're in the active context.
for definition_name in inherited_definition_names:
    parent_definition = get_active_context().get_definition_by_name(definition_name)
```

## Modeling Inheritance in 0.1.3 or Earlier Versions
While inheritance is not explicitly supported in version `0.1.3`, motivated users can recreate the mechanisms for their plugins.

### Recreate the Schema Changes
The first step will be alter the `schema` definition to support inheritance as mentioned in the [supporting changes](#modeling-inheritance-in-013-or-earlier-versions) section above.

Extend the schema structure to include the new `inherits` field:
```yaml
ext:
   name: SchemaInheritanceExtension
   type: schema
   schemaExt:
      add:
        - name: inherits
          type: reference[]
```

### Accessing the Inherited Fields
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
