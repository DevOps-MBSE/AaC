# Check Arguments Against Constraint Definition
`Check Arguments Against Constraint Definition` is a Schema Constraint.
It checks the arguments provided to a constraint by looking up the associated constraint definition and ensuring the
arguments provided in the assignment match the `arguments` defined in the constraint definition.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 1128-1147
    :emphasize-lines: 12-13, 19-20
```

In the above example, `Check Arguments Against Constraint Definition` is applied to the `PrimitiveConstraintAssignment` definition to ensure the `arguments` field matches the expected `arguments` from the primitive constraint definition it is being assigned to.  If the argument is not recognized by the primitive constraint, `Check Arguments Against Constraint Definition` will fail.
