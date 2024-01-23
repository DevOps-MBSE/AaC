# If True Then Empty

`If True Then Empty` is a Schema Constraint that checks to ensure the `empty_field_name` is empty if `bool_field_name` is true.

## Usage Example
```yaml
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
```
In the above example, if `alpha` is set to true, `beta` must be empty.


```yaml
one:
    name: good_data
    alpha: true
```
This set of data would pass the `If True Then Empty` constraint, because `beta` is not defined.


```yaml
one:
    name: bad_data
    alpha: true
    beta:
        - one
        - two
```
This set of data would fail the `If True Then Empty` constraint, because `beta` is defined.