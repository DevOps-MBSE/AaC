# Root Key Names Are Unique
'Root Key Names Are Unique' is a Context Constraint that checks every definition to ensure there are no duplicate root keys defined in the AaC language.

```yaml
schema:
  name: One
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
---
schema:
  name: Two
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
```

The above example would fail the 'Root Key Names Are Unique' because both schemas have the same root.

```yaml
schema:
  name: One
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
---
schema:
  name: Two
  package: test.root_keys
  root: two
  fields:
    - name: name
      type: string
```
In this example, both schemas have unique roots, and so would pass this constraint.