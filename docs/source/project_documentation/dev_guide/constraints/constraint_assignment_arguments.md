# Check Arguments Against Constraint Definition
`Check Arguments Against Constraint Definition` is a Schema Constraint.
It checks the argument by looking up the defined constraint definition and ensuring the
arguments provided in the assignment match the arguments defined in the constraint definition.


## Usage Example
```{eval-rst}
.. literalinclude:: ../../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 1123-1142
    :emphasize-lines: 12-13
```

In the above example, `Check Arguments Against Constraint Definition` is used to ensure the `arguments` field matches the primitive constraint it is being assigned to.  If the type is not interpretable by the primitive constraint, `Check Arguments Against Constraint Definition` will fail.
