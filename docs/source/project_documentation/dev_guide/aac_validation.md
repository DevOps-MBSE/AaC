# What is Validation in the AaC Language?
Because the AaC DSL is leveraging plain-text YAML as the underpinning of the DSL, there is little to no functionality to guide users in the correctness of their YAML AaC structures. AaC has implemented a self-validating language feature so that users can reference which rules are applied to which AaC DSL components, and so that users can define validation for their own user-defined structures. To this end, AaC employs a plugin-based validator system where plugins provide Python-based validator implementations that can be referenced and applied to definitions in the AaC DSL.

Validation rules in AaC are defined with the `validation` definition, which are required to have a corresponding implementation, called a validator plugin. This enables AaC's self-validating mechanism even though YAML is just a markup language.

## Validating the AaC Language
The overall validation mechanism follows this flow:
1. A definition is identified as needing to be validated
2. The definition is parsed for any nested AaC structures
  a. For example, fields in `schema.fields` will trigger the `Field` schema's validation rules.
3. For all of identified AaC structures, each is checked for any `validation` entries
4. For each `validation` entry -- the corresponding `schema` for the substructure and the definition being validated are passed to the corresponding validator plugin
  a. Every instance of `Field` in our example `schema` definition is validated against the rule `Type references exist`
5. Once all of the components of the definition with validation rules are validated, any violations are reported as validation errors.
6. All validation errors from all of the validation rules are collected and returned together
  a. If there are no errors, the definition successfully validates
  b. If there are errors, the definition fails validation

## Validation Definitions
In order for users to document the self-validating constraints in the AaC DSL, they have to declare validation rules via `validation` definitions. These definitions also provide contextual information for the validation as well as behaviors and acceptance criteria -- something to leverage for automatically generating functional/integration tests in the future.


Here is an example `validation` definition:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/validators/exclusive_fields/exclusive_fields.yaml
    :language: yaml
```

Each `validation` definition is required to have a corresponding a Python implementation, which can be seen as a valdiation rule in the `Validation` schema definition:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/spec/spec.yaml
    :language: yaml
    :lines: 120-149
    :emphasize-lines: 24-25
```

## Validator Plugins
Each validator plugin provides its validation function to the core package via pluggy hooks. Each validator plugin should provide one validation function with the following signature:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/validators/exclusive_fields/_validate_exclusive_fields.py
    :language: python
    :pyobject: validate_exclusive_fields
    :lines: 1-18
```

The internal logic of the function is up to the user, but the plugins generally follow the idea of:
1. Extract all instances of the `target_schema_definition` from the `definition_under_test`
2. For each instance of the target schema, which is represented as a dictionary, apply your validation specific logic
3. If the definition under test doesn't meet the constraints of the validator, register and return an error message

For more information on creating and utilizing validator plugins, please view the [Validation Plugins for Developers](validation_plugins).