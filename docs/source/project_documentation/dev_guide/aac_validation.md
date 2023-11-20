# What is Validation in the AaC Language?
Because the AaC DSL is leveraging plain-text YAML as the underpinning of the DSL, there is little to no functionality to guide users in the correctness of their YAML AaC structures. AaC has implemented a self-validating language feature so that users can reference which rules are applied to which AaC DSL components, and so that users can define validation for their own user-defined structures. To this end, AaC employs a plugin-based validator system where plugins provide Python-based validator implementations that can be referenced and applied to definitions in the AaC DSL.

Data structure, or `schema`, validation rules in AaC are defined with the `validation` definition, which require a corresponding implementation, called a validator plugin. The validator plugin is what enables AaC's self-validating mechanism even though YAML is just a markup language. Each data structure is decomposed into its smaller structures, and then the structural constraints (validations) are applied. It is worth keeping in mind that, currently, we make no guarantees regarding the order in which validations are applied. Additionally, AaC also provides the ability to validate primitive types. Primitive validations are distinct from schema validations, but they work in the same general way -- when definitions are validated, any fields with a 'Primitive' type (e.g. string, number, boolean, etc) are validated against the corresponding primitive type validator, if it exists. If no such primitive type validator exists, then the type is treated as a string having a valid value, regardless of the actual value.

Adhereing to AaC's goal of extensibility, users are capable of building plugins that contribute both schema and primitive validations. To read more on how those are created, check out the page on [creating validation plugins](../validation_plugins/).

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

## Schema Validation
### Validation Definitions
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

### Definition Validator Plugins
Each plugin can register multiple definition validators, each of which provides a validation function that's used to validate any corresponding definition structures. It's recommended that plugins have a small, narrow scope of responsibility by focusing on a single validation, but multiple validators can be registered. Definition validators are registered via the plugin function `plugin.register_definition_validations(...)`

Each schema validator must implement a validation function with the following signature/interface:

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

## Primitive Validation
Primitive validation is AaC's way of enforcing constraints for 'Primitive' types such as `integer`, `number`, `file`, `date`, `string`, things that don't need a separate data structure to be represented effectively. All primitive types in the core AaC language have (or will have in coming releases) corresponding primitive validations in the first party plugin [`primitive-type-check`](https://github.com/jondavid-black/AaC/tree/main/python/src/aac/plugins/first_party/primitive_type_check)

### Primitive Validator Plugins
Each plugin can register multiple primitive validators, each of which provides a validation function that's used to validate a corresponding primitive type. Primitive validators are registered via the plugin function `plugin.register_primitive_validations(...)`.

Each primitive validator should provide one validation function with the following signature:
```python
def validate_primitive(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a validator finding if the value under test isn't the expected primitive type.
    This validator returns an error if the value is not compliant with the primitive type.
    Args:
    - definition: The definition of the value to validate.
    - value_to_validate: The value to validate.
    Returns:
    - A validator finding for the given value.
    """
```