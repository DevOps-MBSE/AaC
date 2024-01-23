# No Extension For Final
'No Extension For Final' is a Schema Constraint that checks every schema for extension entries that are marked with a final modifier.

```yaml

schema:
  name: TestSchema
  package: test_aac.plugins.no_ext_for_final
  modifiers:
    - final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
---
schema:
  name: TestChild
  package: test_aac.plugins.no_ext_for_final
  extends: 
    - name: TestSchema
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""
```

In the above example, 'TestChild' is extending 'TestSchema'.  'TestSchema' has the final modifier, meaning that any schema that extends it will fail the 'No Extension For Final' constraint.