# If True Then Empty

`If True Then Empty` is a Schema Constraint that checks to ensure the `empty_field_name` is empty if `bool_field_name` is true.

## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 30-47
```

In the above example, if `alpha` is set to true, `beta` must be empty.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 51-55
```
This set of data would pass the `If True Then Empty` constraint, because `beta` is not defined.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/if_true_then_empty/test_if_true_then_empty.py
    :language: yaml
    :lines: 66-73
```
This set of data would fail the `If True Then Empty` constraint, because `beta` is defined.