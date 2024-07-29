# AaC Inheritance

Version `0.4.0` changed how inheritance works in AaC.  AaC now provides a more "standard" inheritance construct within the `schema` data declaration using the `extends` field.  By "standard", we mean you can extend your `schema` in the same way you would extend a Python class since AaC uses Python under the hood.

In short, you can extend schemas using an object-oriented mindset.  That said, this only applies to `schema`.  While it is technically possible to extend an `Enum` in Python, AaC does not support `enum` extension.  This may be revisited in the future, but initial attempts to support Enum extension in the underlying Python code generation did not work.  And of course, extending primitives is not a thing, but you can define new primitives.

## Modeling AaC Inheritance

Let's take a look at how AaC supports `Schema` inheritance.

Example AaC Schema extension:
```{eval-rst}
.. literalinclude:: ../../../../../python/features/shapes/shapes.aac
    :lines: 1-10
    :language: yaml
```

We've defined a generic `Shape` schema above.  All shapes have a perimeter and area value, so the generic `Shape` schema also has a perimeter and area field.  Shapes which inherit from `Shape` will also inherit these fields.
Below, we will define other schemas which inherit from `Shape`:

```{eval-rst}
.. literalinclude:: ../../../../../python/features/shapes/shapes.aac
    :lines: 12-48
    :language: yaml
```

Each of the above schemas have their own properties that help distinguish them as their specific shape. But they all require a perimeter and area field as a valid shape, and so inherit from `Shape`.

## Inheritance Modifiers

Just as in most programming languages, the AaC language provides some basic modifiers to control what you can and can't do with inherited `schema` definitions.

- `abstract` - This attribute allows declaring a schema as an abstract type. This means it cannot be "instantiated" directly in a definition.  In AaC, this means the schema is either a root type or field in another `Schema`.
- `final` - This allows declaring a schema as a final type, meaning it cannot be extended by another `Schema`.  In AaC this means the final schema cannot appear in another schema's extends field.

To use these inheritance modifiers you simply add them to the `modifiers` field of the `schema`.  Let's take another look at the above example to see how it works:

```{eval-rst}
.. literalinclude:: ../../../../../python/features/shapes/shapes.aac
    :lines: 1-10
    :emphasize-lines: 4-5
    :language: yaml
```

As you can see, the `Shape` schema has an `abstract` modifier.  This means that `Shape` can no longer be instantiated on its own.  To make a shape, you must create or use a schema which inherits from `Shape`.

```{eval-rst}
.. literalinclude:: ../../../../../python/features/shapes/shapes.aac
    :lines: 51-64
    :emphasize-lines: 6-7
    :language: yaml
```

The above `square` schema inherits from Shape as well, but it has a `final` modifier.  This means that no other schema can inherit from Square.

### Using Inheritance

Now that we can define inheritance, how can we use it.  The intended use case is to allow polymorphism in your field declaration.  Let's look at another example to explain.

```{eval-rst}
.. literalinclude:: ../../../../../python/features/shapes/shapes.aac
    :lines: 72-79
    :language: yaml
```

The above pattern schema has a `shapes` field which takes in a number of shapes to create a pattern with.
Since we cannot instantiate the `Shape` schema on its own, we must use a schema which extends `Shape`.  Since the field takes in any `Shape`, however, we can use any schema which extends `Shape`.
