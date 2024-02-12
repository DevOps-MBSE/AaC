# Root Schema Has Name
`Root Schema Has Name` is a Schema constraint that checks every schema with a root key and ensures there is a field called `name`.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 46-51
```

In the above example, `test_schema` does not have a field called `name`, and would fail the `Root Schema Has Name` constraint. To pass this constraint, a field called `name` would need to be added.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 35-42
    :emphasize-lines: 5-6
```
In this example, a `name` field has been added, allowing it to pass the constraint.
