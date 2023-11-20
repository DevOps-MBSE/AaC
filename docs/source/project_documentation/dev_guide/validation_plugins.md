# Validation Plugins for Developers

## Plugin-provided Validations
AaC's approach to validation leverages the larger AaC plugin mechanism to provide a plug-and-play system for creating structural and primitive type validations (constraints) that are used to detect errors and possible issues in systems modeled with AaC.

AaC makes use of two classes of plugin-provided validations: definition validations and primitive validations. The [definition validations](#definition-validations) are used to validate the structural parts of definitions such as required fields while [primitive validations](#primitive-validations) check that values in primitive fields adhere to the expectations of the data type such as checking that values listed as integers are, in fact, integers.

There is also a section listing out the `validation` plugin for the implementation of a validator plugin for 1st and/or 3rd party plugins

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

Primitive validations are handled after the structural validation by the below function:

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

The messages that are returned by the `ValidatorResult` object are formatted according to the severity of the validation issues.
However, the severity and cases for those severities can be outlined as such:

1. **Errors**: These are for errors in the validation and should be taken care of to continue processing further.
2. **Warnings**: These are warnings, the validation will not fail perse, but should be resolved to align the definition to the projects standard.
   1. The reason that warnings should be taken care of is that they can cause issues further down the line of development for your AaC Plugins.
3. **Informational**: These are informational messages that are displayed as a general informative basis.

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

## Implementation of a Validation Plugin for Primitive Types

Examples of a primitive validator plugin can be found by refering the first-party provider for primitive validations [primitive-type-check](https://github.com/jondavid-black/AaC/tree/main/python/src/aac/plugins/first_party/primitive_type_check)

Looking inside this directory, the structure of this plugin looks like other AaC plugins:

```markdown
.primitive_type_check
├── __init__.py
├── validators
   ├── __init__.py
   ├── bool_validator.py
   ├── date_validator.py
   ├── file_validator.py
   ├── int_validator.py
   └── num_validator.py
└── primitive_type_check.yaml
```

Seeing the structure of this validator, there is an `init` module, there are a number of implementations in the `validators` package, and the `yaml` file used to describe the plugin.

Taking a look at the bool validator we'll see the primitive validator interface:

```python
def validate_bool(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a Validation finding if the type isn't valid, otherwise None.
    This function is intended to be used in the Validation apparatus, and for this result
    to be collated with other finding into a larger ValidatorResult.
    Arge:
        definition (Definition): The definition that the value belongs to.
        value_to_validate (Any): The value to be tested.
    Returns:
        A ValidatorFinding if the value is not a boolean or None.
    """

    is_invalid = not isinstance(value_to_validate, bool)
    finding = None
    if is_invalid:
        lexeme, *_ = [lexeme for lexeme in definition.lexemes if lexeme.value.lower() == str(value_to_validate.lower())]
        finding_message = f"{value_to_validate} is not a valid value for boolean type {PRIMITIVE_TYPE_BOOL}."
        finding_location = FindingLocation.from_lexeme(BOOL_VALIDATION_NAME, lexeme)
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
```

The yaml for the plugin looks like any other plugin definition file:

```yaml
model:
  name: primitive-type-checking
  description: |
    Primitive Type Checking is an Architecture-as-Code plugin that provides
    primitive type validations for the primitive enum types defined in the core specification.
  behavior:
    ...
    - name: Validate Boolean Primitives
      type: request-response
      description:
      input:
        - name: input
          type: ValidatorInput
      output:
        - name: results
          type: ValidatorOutput
      acceptance:
        - scenario: Successfully Validate a Boolean Primitive Value
          given:
            - The ValidatorInput content consists of valid AaC definitions
            - The ValidatorInput contains at least one definition field that is defined as being type `bool`
            - The value in the primitive `bool` field is a valid boolean YAML value
          when:
            - The input is validated
          then:
            - The ValidatorOutput does not indicate any errors
            - The ValidatorOutput does not indicate any warnings
            - The ValidatorOutput indicates the primitive value under test is valid
        - scenario: Fail to Validate an Integer Primitive Value Is a non-boolean String
          given:
            - The ValidatorInput content consists of AaC definitions
            - The ValidatorInput contains at least one definition field that is defined as being type `bool`
            - The value in the primitive `bool` field contains alphabetical letters or punctuation marks that don't represent a YAML boolean value
          when:
            - The input is validated
          then:
            - The ValidatorOutput indicates an error
            - The ValidatorOutput indicates the primitive value under test is invalid
    ...
```

Lastly, the `primitive-type-check` plugin uses the following `Plugin` method `plugin.register_primitive_validations(...)` to register its several primitive validators:
```python
@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.
    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_primitive_validations(_get_primitive_validations()) # <-- This function registers the primitive validators.
    return plugin
```

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
