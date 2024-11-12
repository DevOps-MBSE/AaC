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

This constraint does not check required fields of parent definitions

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/aac.aac
    :language: yaml
    :emphasize-lines: 14, 18
    :lines: 10-33
```
```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/aac.aac
    :language: yaml
    :emphasize-lines: 14, 18
    :lines: 207-239
```
