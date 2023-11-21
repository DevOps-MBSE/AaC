# Validation Plugins for Developers

## General Information surrounding Validation

Any references to code within this document regarding the `validation` plugin can be found here in the AaC project:
`AaC/python/src/validate/_validate.py`

This validator plugin can be separated into the below sections.

1. [Definition Validations](#definition-validations)
2. [Primitive Validations](#primitive-validations)

There is also a section listing out the `validation` plugin for the implementation of a validator plugin for 1st and/or 3rd party plugins

* [Implementation of a Validation Plugin for Definitions](#implementation-of-a-validation-plugin-for-definitions)

It is also worthy to note that the way that the AaC DSL validates itself is through associating user-defined validation definitions with a corresponding python implementation which is used to programmatically test that the validation's constraints are met. The validation process is entirely data-driven, so with this implementation it can validate the data in the definition via the very constraints.that are defined as part of the definition.

## Definition Validations

The following snippet shows how the `_validate.py` validates a `definition` that is being passed through:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/validate/_validate.py
    :language: python
    :pyobject: _validate_definition
```

The above snippet this shows an example of how the validator takes in a `Definition`, a list of validator plugins, as well as the `LanguageContext` that provides the context to validate the definition within. The `Definition` validations can be alternative described as *Structural Constraints* for data structures (schema definitions). With this in mind the `Definition` validation will take a target `Definition` and decompose it into its `sub-definition`s, other definitions that are components of schema definitions (e.g. `Field` in `schema`). These `sub-structure`s are then validated by passing each sub-structure and corresponding values to the appropriate validator, defined by the validations of each sub-structure, which may produce finding(s) that are returned to the user via the `ValidatorResult` object.

This approach is also used for in the [Primitive Validations](#primitive-validations), but primitive validation only targets fields defined in the `Primitives` enum definition.

## Primitive Validations

Primitive Validations are handled by the below function:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/validate/_validate.py
    :language: python
    :pyobject: _validate_field_types
```

The above method, like the `_validate_definition` function outlined in the previous example, takes in a `Definition` and takes in the `LanguageContext` of the definition that is being validated. However, The primary goal of this snippet is to validate the *Primitive and Enum Types* of a definition schema and pass these results to the `ValidatorResult` object for further processing and eventual output to the user. This function is an example of a *Primitive Constraint* with how validations are made/applied.

The results of this validation are consolidated with the results from the `_validate_definition` function above in the `ValidatorResult` object for further analysis and output for the user to discern.

## Purpose of the Validation Definition

Outlined in the code sample below is the schema of the `Validation Definition`.

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/spec/spec.yaml
    :language: yaml
    :lines: 120-149
```

The arguments that are passed through this `Validation` Definition are three variables:

1. The `name` of the `definition` being validated.
2. The `description` of the `definition` being validated.
3. The `behavior` of the `definition` that is being validated.

So the validation is taking the `definition` and is checking to make sure that the proper fields, and the arguments that are being passed are there in the declaration of the `definition` being validated.

For example, in our enum schema, we have a validation that is making sure there are fields in the arguments are there in the definition.

## Meanings of Validation Messages

After validation occurs, a `ValidatorResult` object will return the results of the validation and compile the results into single message.  A `ValidatorResult` will contain a list of definitions that were validated, and a `ValidatorFindings` object which contains all `ValidatorFinding` objects returned by the validation.

A `ValidatorFinding` is returned when the validator wants to provide feedback of some kind.  A failed validation or error message is one type of feedback that can be provided, but it does not have to be limited to that.  As such, a `FindingSeverity` object is included to inform how severe the finding is. 

The messages that are returned by the `ValidatorResult` object are formatted according to the severity of the validation issues.
However, the severity and cases for those severities can be outlined as such:

1. **Errors**: These are for errors in the validation and should be taken care of to continue processing further.
2. **Warnings**: These are warnings, the validation will not fail perse, but should be resolved to align the definition to the projects standard.
   1. The reason that warnings should be taken care of is that they can cause issues further down the line of development for your AaC Plugins.
3. **Informational**: These are informational messages that are displayed as a general informative basis.

A `FindingLocation` object will also be returned, which contains the source file and line number where the finding occurred. 

## Implementation of a Validation Plugin for Definitions

### Creating a Validation Plugin for Definitions

Examples of a validator plugin can be found in the below directory:
[AaC/python/src/aac/plugins/validators/](https://github.com/DevOps-MBSE/AaC/tree/main/python/src/aac/plugins/validators)

Taking a look at the `required_fields` validator, we will use this as an example of what is required for a validator plugin.

Looking inside this directory the structure of this validator looks like this:

```markdown
.required_fields
├── __init__.py
├── _validate_required_fields.py
└── required_fields.yaml
```

So seeing the structure of this validator, there is an `init`, `implementation_file` and the `yaml` file used to create the initial plugin configuration.

Taking a look at the `implementation_file` (`_validate_required_fields.py`) and `required_fields.yaml`:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/validators/required_fields/_validate_required_fields.py
    :language: python
    :pyobject: validate_required_fields
```

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/validators/required_fields/required_fields.yaml
    :language: yaml
```

***NOTE***: Without the `implementation_file` the initial validator plugin will spit out an error saying that an implementation file is missing. This is needed for the validator plugin to function properly.


## Validation Interface & Validator Development Best Practices

### Expected Arguments for the Validation Interface

The Validation Interface that is being used is based on arguments that are passed to the validator plugins.

As long as the arguments that are passed through the validator plugins and the returned types are similar then the plugins that are created/used can be used interchangeably and can be utilized based on the usecase.

An example of one of the validator plugins is the `bool_validator.py` plugin that can be found in the `AaC/python/src/aac/plugins/first_party/primitive_type_check/validators/`

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/first_party/primitive_type_check/validators/bool_validator.py
    :language: python
    :pyobject: get_validator
```

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/first_party/primitive_type_check/validators/bool_validator.py
    :language: python
    :pyobject: validate_bool
```

The return of this validator plugin is the `finding` from the `validate_bool` function. The arguments that are passed through are, the `Definition` and the type of the `value_to_validate` which is checking if the boolean that is being passed is valid.

Another validator is the `_validate_exclusive_fields.py` plugin which checks and validates the fields of the definition or schema. An example snippet of the arguments passed are as follows:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/validators/exclusive_fields/_validate_exclusive_fields.py
    :language: python
    :pyobject: validate_exclusive_fields
    :lines: 1-18
```

Since this plugin is a part of the validator as a whole, it differs slightly from the `bool_validator.py` plugin that is a part of the `primitive_type_check` plugin.

The arguments that are being passed through are similar, `Definition`, `LanguageContext`, and then any additional `validation_args`. As seen in the `_validate.py` validator the arguments and the return are quite similar.

As mentioned before, the `ValidatorResult` will return the results of the validator from the functions that are being invoked, through the validation process, and compile the results into a final message that notifies the user of any `errors`, `warnings` or relevant informational messages regarding the validation.

### Best Practices for Validation Plugin Development

Best practices for the Validation Plugin Development is to do the following:

1. Keep the scope of the validator plugin small in scope; This allows for some flexibility and ease of testing the plugin.
2. Use `arguments`; They allow for some flexibility for what can be validated.
3. Unit Tests are your friend; Using Unit Tests allows for better testing of the validator plugin itself. This will help in identifying issues or unforeseen problems with the new plugin.
