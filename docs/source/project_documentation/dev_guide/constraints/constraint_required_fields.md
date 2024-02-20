# Required Fields
`Required Fields` is a Schema Constraint that checks if a field is required, and confirms that required fields are defined.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 17-33
    :emphasize-lines: 6, 12, 17
```
In the above example, the fields `name` and `package` are required, and the field `description` is not required.  If `name` or `package` are not defined, it will fail the `Required Fields` constraint.