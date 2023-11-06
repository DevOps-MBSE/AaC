---
layout: default
title: AaC Inheritance
parent: Language API
nav_order: 3
has_children: false
---
# AaC Inheritance

Version `0.4.0` changed how inheritance works in AaC.  AaC now provides a more "standard" inheritance construct within the `Schema` data declaration using the `extends` field.  By "standard", we mean you can extend your `Schema` in the same way you would extend a python class since AaC uses python under the hood.  In short, you can extend schemas using an object-oriented mindset.  That said, this only applies to `Schema`.  While it is technically possible to extend an `Enum` in python, AaC does not support `enum` extension.  This may be revisited in the future, but initial attempts to support Enum extension in the underlying python code generation did not work.  And of course, extending primitives is not a thing (but you can define new primitives).

## Modeling AaC Inheritance

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

## Inheritance Modifiers

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

### Using Inheritance

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
