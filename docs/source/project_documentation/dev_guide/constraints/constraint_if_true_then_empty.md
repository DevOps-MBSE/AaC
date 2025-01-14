# If True Then Empty

`If True Then Empty` is a Schema Constraint that checks to ensure the `empty_field_name` is empty if `bool_field_name` is true.

## Usage Example
In the below example, if `alpha` is set to true, `beta` must be empty.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 36-53
    :emphasize-lines: 15-18
```

The following set of data would pass the `If True Then Empty` constraint, because `beta` is not defined.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 58-60
    :emphasize-lines: 3
```

The following set of data would pass the `If True Then Empty` constraint, because `alpha` is set to `false` allowing `beta` to be defined.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 64-69
    :emphasize-lines: 3-6
```

The following set of data would fail the `If True Then Empty` constraint, because `alpha` is set to `true` and `beta` is defined.
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 73-78
    :emphasize-lines: 3-6
```
