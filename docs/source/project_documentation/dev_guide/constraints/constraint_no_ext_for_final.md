# No Extension For Final
`No Extension For Final` is a Schema Constraint that checks every schema for extension entries that are marked with a `final` modifier.

## Usage Example
In the below example, `TestChild` is validly extending `TestParent`.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/no_ext_for_final/test_no_ext_for_final.py
    :language: yaml
    :lines: 59-78
    :emphasize-lines: 11, 13-15
```

However, in this example `TestParent` now has the `final` modifier, so defining `TestChild` as an extension is invalid and will fail the `No Extension For Final` constraint.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/no_ext_for_final/test_no_ext_for_final.py
    :language: yaml
    :lines: 82-103
    :emphasize-lines: 4-5, 13, 15-17
```
