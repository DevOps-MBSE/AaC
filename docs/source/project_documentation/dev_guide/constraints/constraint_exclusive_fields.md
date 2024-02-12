# Mutually Exclusive Fields
`Mutually Exclusive Fields` is a Schema Constraint.
It ensures that, out of a set of fields, only one field is defined at any time.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 39-59
    :emphasize-lines: 9-14, 19-21
```
In the above example, only one of the fields (`alpha`, `beta`, and `gamma`) can be defined.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 64-66
    :emphasize-lines: 66
```
Here, `alpha` is the only one defined.  This would pass the `Mutaully Exclusive Fields` constraint.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 82-85
    :emphasize-lines: 3-4
```
Here, both `alpha` and `beta` are defined, which would fail the `Mutaully Exclusive Fields` constraint.
