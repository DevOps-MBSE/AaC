# Mutually Exclusive Fields
`Mutually Exclusive Fields` is a Schema Constraint that. 
It ensure only one of the fields are defined at any time.


## Usage Example

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
```
In the above example, only one of the fields (`alpha`, `beta`, and `gamma`) can be defined.

```yaml
one:
    name: good_data
    alpha: alpha
```
Here, `alpha` is the only one defined.  This would pass the `Mutaully Exclusive Fields` constraint.

```yaml
one:
    name: bad_data
    alpha: alpha
    beta: beta
```
Here, both `alpha` and `beta` are defined, which would fail the `Mutaully Exclusive Fields` constraint.