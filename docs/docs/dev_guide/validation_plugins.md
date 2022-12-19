---
layout: default
parent: Developer's Guide to AaC
title: Validation Plugins for Developers
nav_order: 7
has_children: false
---

# Validation Plugins for Developers

## Plugin Validations

### General Information surrounding Validation

Any references to code within this document regarding the `validation` plugin can be found here in the AaC project:
`AaC/python/src/validate/_validate.py`

This validator plugin can be separated into the below sections.

1. [Definition Validations](#definition-validations)
2. [Primitive Validations](#primitive-validations)

There is also a section listing out the `validation` plugin for the implementation of a validator plugin for 1st and/or 3rd party plugins

* [Implementation of a Validation Plugin for Definitions](#implementation-of-a-validation-plugin-for-definitions)

It is also worthy to note that the ways that AaC validates is that ituses a self validating implementation. The validation is entirely data-driven, so with this implementation it can validate based on data present/provided in the definition(s).

### Definition Validations

The following snippet shows how the `_validate.py` validates a `definition` that is being passed through:

```python
 def _validate_definition( 
     definition: Definition, validator_plugins: list[DefinitionValidationContribution], language_context: LanguageContext 
 ) -> list[ValidatorResult]: 
     """Traverse the definition and validate it according to the validator plugins.""" 
  
     validator_results = [] 
  
     applicable_validator_plugins = get_applicable_validators_for_definition(definition, validator_plugins, language_context) 
     ancestor_definitions = get_definition_ancestry(definition, language_context) 
     sub_structure_definitions = get_definition_schema_components(definition, language_context) 
     all_applicable_definitions = ancestor_definitions + sub_structure_definitions 
  
     for target_schema_definition in all_applicable_definitions: 
         sub_definition_validations = target_schema_definition.get_validations() 
  
         if sub_definition_validations: 
             for validation in sub_definition_validations: 
                 validation_name = validation.get(DEFINITION_FIELD_NAME) 
                 validator_plugin = list(filter(lambda plugin: plugin.name == validation_name, applicable_validator_plugins)) 
  
                 if validator_plugin: 
                     validator_results.append( 
                         _apply_validator(definition, target_schema_definition, language_context, validator_plugin[0]) 
                     ) 
  
     validator_results.append(_validate_primitive_types(definition, language_context)) 
     return validator_results 
```

With the above snippet this shows an example of how the validator is taking in a `Definition`, a list of other validator plugins, as well as, the `LanguageContext` of the definition that is being validated. The `Definition` validation is limited by *Structural Constraints*. With this in mind the`Definition` validator will take a `definition` that is being passed in and will decompose it into its `sub-definition`s within the primary schema. With this, this validator will take a definition and filter it down by the structures that are present within. These `sub-structure`s are then validated by what is already present in the primary `definition` then all these are run through and passed to the `ValidatorResult` object.

`ValidatorResult` object is then parsed through and returned to the user through some output of the latter results. This is also done for the below example in [Primitive Validations](#primitive-validations), but it is primarily targeted towards the `Primitive Types` within the `Definition`s.

### Primitive Validations

Primitive Validations are passed into the below function:

```python
def _validate_primitive_types(definition: Definition, language_context: LanguageContext) -> ValidatorResult: 
     """Validates the instances of AaC primitive types.""" 
     findings = ValidatorFindings() 
     definition_schema = get_definition_schema(definition, language_context) 
     if definition_schema: 
         findings.add_findings(_validate_fields(definition, definition_schema, definition.get_top_level_fields(), language_context)) 
  
     return ValidatorResult([definition], findings) 

```

The above method like the `_validate_definition` function outlined in the previous example takes in a `Definition` and takes in the `LanguageContext` of the defintion that is being validated. However, The primary goal of this snippet is to validate the *Primitive Types* of a definition schema and pass these results to the `ValidatorResult` object for further processing and eventual output to the user. This function is an example of a *Primitive Constraint* with how validations are made/applied.

The results of this validation are also coinsiding with the results from the `_validate_definition` function above and the results are taking in together to the `ValidatorResult` object for further analysis and output for the user to discern.

### Purpose of the Validation Definition

Outlined below is the `validator_implementation` plugin file. The purpose of this plugin is to verify that the 1st and 3rd party plugins have a working python plugin implementation. This also will verify that the `Definition` has a proper implementation also.

```yaml
validation: 
   name: Validation definition has an implementation 
   description: Verifies that every validation definition has a corresponding python plugin implementation 
```

### Meanings of Validation Messages

The messages that are returned by the `ValidatorResult` object are formatted according to the severity of the validation issues.
However, the severity and cases for those severities can be outlined as such:

1. **Errors**: These are for errors in the validation and should be taken care of to continue processing further.
2. **Warnings**: These are warnings, the validation will not fail perse, but should be resolved to align the definition to the projects standard.
   1. The reason that warnings should be taken care of is that they can cause issues further down the line of development for your AaC Plugins.
3. **Informational**: These are informational messages that are displayed as a general informative basis.

## Implementation of a Validation Plugin for Definitions

### Creating a Validation Plugin for Definitions

Examples of a validator plugin can be found in the below directory:
`AaC/python/src/aac/plugins/validators/`

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

```python
"""   _validate_required_fields.py   """
def validate_required_fields(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the definition has all required fields populated.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    required_field_names = validation_args
    schema_defined_fields_as_list = target_schema_definition.get_top_level_fields().get("fields") or []
    schema_defined_fields_as_dict = {field.get("name"): field for field in schema_defined_fields_as_list}

    def validate_dict(dict_to_validate: dict) -> None:
        for required_field_name in required_field_names:
            field_value = dict_to_validate.get(required_field_name)
            field_type = schema_defined_fields_as_dict.get(required_field_name, {}).get("type")

            if field_value is None:
                missing_required_field = f"Required field '{required_field_name}' missing from: {dict_to_validate}"
                findings.add_error_finding(definition_under_test, missing_required_field, PLUGIN_NAME, 0, 0, 0, 0)
                logging.debug(missing_required_field)

            elif not _is_field_populated(field_type, field_value):
                unpopulated_required_field = f"Required field '{required_field_name}' is not populated in: {dict_to_validate}"
                findings.add_error_finding(definition_under_test, unpopulated_required_field, PLUGIN_NAME, 0, 0, 0, 0)
                logging.debug(unpopulated_required_field)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)


def _is_field_populated(field_type: str, field_value: Any) -> bool:
    """Return a boolean indicating is the field is considered 'populated'."""
    is_field_array_type = is_array_type(field_type)
    is_field_populated = False

    if is_field_array_type:
        is_field_populated = len(field_value) > 0
    elif type(field_value) is bool:
        is_field_populated = field_value is not None
    elif field_value:
        is_field_populated = True

    return is_field_populated
```

```yaml
# required_fields.yaml
validation:
  name: Required fields are present
  description: Verifies every field declared as required is present and populated
  behavior:
    - name: Verify that definition fields marked as required are populated.
      type: request-response
      input:
        - name: input
          type: ValidatorInput
      output:
        - name: results
          type: ValidatorOutput
      acceptance:
        - scenario: Successfully Validate a definition's required fields
          given:
            - The ValidatorInput content consists of valid AaC definitions.
            - The ValidatorInput contains some AaC definitions that reference other definitions.
          when:
            - The input is validation
          then:
            - The ValidatorOutput does not indicate any errors
            - The ValidatorOutput does not indicate any warnings
            - The ValidatorOutput indicates the validator plugin under test is valid
        - scenario: Fail to validate a definition's required fields
          given:
            - The ValidatorInput content consists of otherwise valid AaC definitions.
            - The ValidatorInput contains at least one field that is required.
            - The ValidatorInput contains at least one required field that is missing.
          when:
            - The ValidatorInput is validated
          then:
            - The ValidatorOutput has errors
            - The ValidatorOutput errors indicate that there are missing required fields
```

***NOTE***: Without the `implementation_file` the initial validator plugin will spit out an error saying that an implementation file is missing. This is needed for the validator plugin to function properly.


## Validation Interface & Validator Development Best Practices

### Expected Arguments for the Validation Interface


### Best Practices for Validation Plugin Development

Best practices for the Validation Plugin Development is to do the following:

1. Keep the scope of the validator plugin small in scope; This allows for some flexibility and ease of testing the plugin.
2. Use `arguments` to validate; This allows for some flexibility for what can be validated.
3. Unit Tests are your friend; Using Unit Tests allows for better testing of the validator plugin itself. This will help in identifying issues or unforseen problems with the new plugin.
