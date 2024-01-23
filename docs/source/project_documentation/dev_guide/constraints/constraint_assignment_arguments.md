# Check Arguments Against Constraint Definition
'Check Arguments Against Constraint Definition' is a Schema Constraint. 
It checks the argument by looking up the defined constraint name definition and ensuring the
arguments provided in the assignment match the arguments defined in the constraint definition.

```yaml
schema:
  name: PrimitiveConstraintAssignment
  package: aac.lang
  description: |
    Assigns a primitive constraint to a primitive definition.
  fields:
    - name: name
      type: dataref(plugin.primitive_constraints.name)
      description: |
        The name of the schema constraint definition.
      is_required: true
    - name: arguments
      type: any
      description: |
        Arguments for the primitive constraint if applicable.  Using the any type
        because the arguments are defined by the constraint definition.  The 
        constraint_assignment_arguments constraint will cross reference arguments
        provided here against the constraint definition.
  constraints:
    - name: Check arguments against constraint definition
```
In the above example, 'Check arguments against constraint definition' is used to ensure the 'arguments' field matches the primitive constraint it is being assigned to.  If the type is not interpretable by the primitive constraint, 'Check arguments against constraint definition' will fail.