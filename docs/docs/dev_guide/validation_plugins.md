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

With the above snippet this shows an example of how the validator is taking in a `Definition`, a list of other validator plugins, as well as, the `LanguageContext` of the definition that is being validated. This would be a good example of a validator with a *Structural Constraint* The `Definition` that is being that is being validated may have a `sub-definition` field within the primary schema. With this in mind, this validator will take a definition and filter it down by the structures that are present within. These `sub-structures` are then validated by what is already present in the primary `definition` then all these are run through and passed to the `ValidatorResult` object.

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

### Validation Definition

### Implementation of the Validator

## Validation Interface

### Expected Arguments for the Validation Interface

## Best Practices for Definition Validation Development

### Scope

### Flexibility

### Unit Tests
