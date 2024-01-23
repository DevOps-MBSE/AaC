# If True Then Empty

'If true then empty' is a Schema Constraint that checks to ensure the 'empty_field_name' is empty if 'bool_field_name' is true.

```yaml
TEST_SCHEMA = """
schema:
    name: IfTrueEmptyTest
    package: test.if_true_then_empty
    root: one
    fields:
        - name: name
          type: string
        - name: alpha
          type: bool
        - name: beta
          type: string[]
    constraints:
        - name: If true then empty
          arguments:
            - name: bool_field_name
              value: alpha
            - name: empty_field_name
              value: beta

"""

GOOD_DATA_1 = """
one:
    name: GoodData1
    alpha: true
"""

BAD_DATA_1 = """
one:
    name: BadData1
    alpha: true
    beta:
        - one
        - two
"""
```

In the above example, alpha is set to true.  To pass the If True Then Empty constraint, beta must be empty.  In the bad data example, beta is defined and would therefore fail the constraint.