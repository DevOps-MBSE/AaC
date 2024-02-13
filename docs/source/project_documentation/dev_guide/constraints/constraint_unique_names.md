# Unique Names
`Unique Names` is a Schema Constraint that checks if a model name is unique within a package.
If two models within the same package share a name, the `Unique Names` constraint will fail.

Models in different packages can have the same name, and different packages can have the same name.  But within the package each model must have a unique name.
