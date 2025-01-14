# Unique Names
`Unique Names` is a Schema Constraint that checks if a model name is unique within a package.
If two models within the same package share a name, the `Unique Names` constraint will fail.

Models in different packages can have the same name, and different packages can have the same name.  But within the package each model must have a unique name.

Here are some example definition groupings.


The first example pair is valid because they are different names, even though they are in the same package, `package_one`.

``` yaml
schema:
  name: model_one
  package: package_one
  description: First example model
---
schema:
  name: model_one_a
  package: package_one
  description: Version a of first example model
```

The second example pair is valid even though they have the same names, because they are in different packages, `package_one` and `package_two`.
``` yaml
schema:
  name: model_one
  package: package_one
  description: First example model package one
---
schema:
  name: model_one
  package: package_two
  description: First example model package two
```

And the third example pair is invalid because they have the same name and are in the same package.
``` yaml
schema:
  name: model_one
  package: package_one
  description: First example model
---
schema:
  name: model_one
  package: package_one
  description: Second example model
```
