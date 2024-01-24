# Mutually Exclusive Fields
`Mutually Exclusive Fields` is a Schema Constraint that. 
It ensure only one of the fields are defined at any time.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 38-60
```
In the above example, only one of the fields (`alpha`, `beta`, and `gamma`) can be defined.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 63-66
```
Here, `alpha` is the only one defined.  This would pass the `Mutaully Exclusive Fields` constraint.


```{eval-rst}
.. literalinclude:: ../../../../../python/tests/test_aac/plugins/exclusive_fields/test_exclusive_fields.py
    :language: yaml
    :lines: 69-72
```
Here, both `alpha` and `beta` are defined, which would fail the `Mutaully Exclusive Fields` constraint.