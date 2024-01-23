# Mutually Exclusive Fields
'Mutually Exclusive Fields' is a Schema Constraint that. 
It ensure only one of the fields are defined at any time.

```yaml
schema:
    name: One
    package: test.exclusive_fields
    root: one
    fields:
        - name: name
          type: string
          is_required: true
        - name: alpha
          type: string
        - name: beta
          type: string
        - name: gamma
          type: string
    constraints:
        - name: Mutually exclusive fields
          arguments:
            fields:
                - alpha
                - beta
                - gamma  

"""

GOOD_DATA_1 = """
one:
    name: GoodOne
    alpha: alpha
"""

BAD_DATA_1 = """
one:
    name: bad
    alpha: alpha
    beta: beta
"""
```

In the above example, only one of the fields(Alpha, Beta, Gamma) can be defined.  In the Good Data, alpha is the only one defined.  In the bad data, both alpha and beta are defined, which would fail the 'Mutaully Exclusive Fields' constraint.