# AaC Inheritance

Version `0.4.0` changed how inheritance works in AaC.  AaC now provides a more "standard" inheritance construct within the `schema` data declaration using the `extends` field.  By "standard", we mean you can extend your `schema` in the same way you would extend a Python class since AaC uses Python under the hood.  

In short, you can extend schemas using an object-oriented mindset.  That said, this only applies to `schema`.  While it is technically possible to extend an `Enum` in Python, AaC does not support `enum` extension.  This may be revisited in the future, but initial attempts to support Enum extension in the underlying Python code generation did not work.  And of course, extending primitives is not a thing, but you can define new primitives.

## Modeling AaC Inheritance

Let's take a look at how AaC supports `Schema` inheritance.

Example AaC Schema extension:
```{eval-rst}
.. literalinclude:: ../../../../../python/features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac
    :language: yaml
```

We've defined a generic person and extended that to an employee which adds the `id` field.  To use these in an AaC model we would do the following:

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

- `abstract` - This allows you to declare your `schema` as an abstract type, meaning it cannot be "instantiated" directly in a declaration.  In AaC you can think of this as either being a root type or field in another `schema`.
- `final` - This allows you to declare your `schema` as a final type, meaning it cannot be extended by another `schema`.  In AaC this means you cannot include the final schema in another `schema`'s `extends` field.

To use these inheritance modifiers you simply add them to the `modifiers` field of the `schema`.  Let's update the previous example to see how this works.

```{eval-rst}
.. literalinclude:: ../../../../python/features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inhertaince_two.aac
    :language: yaml
    :lines: 1-22
    :emphasize-lines: 4-5, 15-16
```

We can no longer instantiate a `Person` because it is now `abstract`.  We would also be prevented from creating something like `SalaryEmployee` that would extend `Employee` because `Employee` has the `final` modifier.

### Using Inheritance

Now that we can define inheritance, how can we use it.  The intended use case is to allow polymorphism in your field declaration.  Let's look at another example to explain.

```{eval-rst}
	.. literalinclude:: ../../../../../python/features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac
	    :language: yaml
	```

We no longer define individuals but teams, and that team includes members that can be made up of `Employee` or `Contractor`.
