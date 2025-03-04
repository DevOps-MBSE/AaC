# Required Fields
`Required Fields` is a Schema Constraint that checks if a field is required, and confirms that required fields are defined.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 17-33
    :emphasize-lines: 6, 12, 17
```
In the above example, the fields `name`, `package`, and `description` are required.  If any of these fields are not defined in a definition, it will fail the `Required Fields` constraint.


> **NOTE**: _This constraint does not check for required fields of parent definitions._

```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 10-33
    :emphasize-lines: 13, 19, 24
```
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 207-239
    :emphasize-lines: 3-5
```

In the above example, `Schema` is an extension of `AaCType`.  So while a `Schema` definition can use the `name`, `description`, and `package` fields from `AaCType`, the `is_required` field does not carry over.  If you want an extension's field to be required, you will have to redefine the field.

