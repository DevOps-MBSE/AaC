# Root Schema Has Name
`Root Schema Has Name` is a Context Constraint that checks every schema with a root key and ensures there is a field called `name`.


## Usage Example
In this example, a `name` field has been added, allowing it to pass the constraint.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 129-136
    :emphasize-lines: 5-6
```

In the below example, `test_schema` does not have a field called `name`, and would fail the `Root Schema Has Name` constraint. To pass this constraint, a field called `name` would need to be added.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 129-132, 135-136

```

In this example, a `name` field has been added, but it is empty triggering, a `LanguageError` in `parse_and_load`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 140-145
    :emphasize-lines: 5
```

In this example, the `name` field is missing, triggering a `LanguageError` in `parse_and_load`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 149-153
```

In this example, the schema `name` field is empty, triggering a `ParserError` in `parse_and_load`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 157-162
    :emphasize-lines: 2
```

In this example, the schema `name` field is missing, triggering a `ParserError` in `parse_and_load`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 166-170
```

In this example, we use two schemas to create a non-unique definition for `AacType` , triggering a `LanguageError` in `root_schema_must_have_name`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/root_schema_must_have_name/test_root_schema_must_have_name.py
    :language: yaml
    :lines: 174-210, 213-222
    :emphasize-lines: 4-5,39-40
```

> ** NOTE ** _The `Unknown Location` and `No file to reference` are valid location returns for the error situations encountered in this constraint._
