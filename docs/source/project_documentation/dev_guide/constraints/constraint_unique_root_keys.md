# Root Key Names Are Unique
`Root Key Names Are Unique` is a Context Constraint that checks every definition to ensure there are no duplicate root keys defined in the AaC language.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/unique_root_keys/test_unique_root_keys.py
    :language: yaml
    :lines: 49-63
    :emphasize-lines: 4
    :emphasize-lines: 12
```
The above example would fail the `Root Key Names Are Unique` because the referenced root `one` has more than one definition of itself.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/unique_root_keys/test_unique_root_keys.py
    :language: yaml
    :lines: 31-45
    :emphasize-lines: 4
    :emphasize-lines: 12
```
In this example, each referenced root has only one definition of itself, and so would pass this constraint.