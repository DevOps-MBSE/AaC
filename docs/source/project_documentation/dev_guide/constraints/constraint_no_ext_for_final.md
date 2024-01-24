# No Extension For Final
`No Extension For Final` is a Schema Constraint that checks every schema for extension entries that are marked with a final modifier.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/no_ext_for_final/test_no_ext_for_final.py
    :language: yaml
    :lines: 60-81
```

In the above example, `TestChild` is extending `TestSchema`.  `TestSchema` has the final modifier, meaning that any schema that extends it will fail the `No Extension For Final` constraint.