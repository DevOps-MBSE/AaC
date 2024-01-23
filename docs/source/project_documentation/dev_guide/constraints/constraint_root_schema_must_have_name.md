# Root Schema Has Name
`Root Schema Has Name` is a Schema constraint that checks every schema with a root key and ensures there is a field called name.


## Usage Example

```yaml
schema:
  name: test_schema
  root: test_root
  fields:
    - name: test_field
      type: string
```

In the above example, `test_schema` does not have a field called `name`, and would fail the `Root Schema Has Name` constraint. To pass this constraint, a field called `name` would need to be added.

```yaml
schema:
  name: test_schema
  root: test_root
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
```
In this example, a `name` field has been added, allowing it to pass the constraint.