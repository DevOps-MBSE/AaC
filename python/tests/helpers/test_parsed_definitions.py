"""
Unit tests for the testing helper parsed_definitions module.
"""

from unittest import TestCase

from aac.parser import parse

from tests.helpers.parsed_definitions import (
    REQUIRED_VALIDATION_STRING,
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
    create_model_definition,
    create_step_entry,
    create_usecase_definition,
    create_validation_entry,
)


class TestArchParsedDefinitions(TestCase):
    """
    Unit test class for testing helper parsed_definitions module.
    """

    def test_create_schema_definition_without_fields_or_required(self):
        definition_name = "Test Name"

        expected_yaml = "\n".join(
            [
                "schema:",
                f"  name: {definition_name}",
                "  description: ''",
                "  fields: []",
                "  required: []",
                "  validation: []",
            ]
        )

        parsed_definition = create_schema_definition(name=definition_name)

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_schema_definition_with_fields_and_required(self):
        definition_name = "Test Name"
        definition_description = "Some description content for the definition"
        field_name = "field1"
        field_description = "description for field 1"
        field_type = "Type1"

        expected_yaml = "\n".join(
            [
                "schema:",
                f"  name: {definition_name}",
                f"  description: {definition_description}",
                "  fields:",
                f"  - name: {field_name}",
                f"    type: {field_type}",
                f"    description: {field_description}",
                "  required:",
                f"  - {field_name}",
                "  validation: []",
            ]
        )

        field_definition = create_field_entry(field_name, field_type, field_description)

        expected_parsed_definition = parse(expected_yaml)[0]
        required_field_validator = create_validation_entry(REQUIRED_VALIDATION_STRING, [field_name])
        actual_parsed_definition = create_schema_definition(
            name=definition_name, description=definition_description, fields=[field_definition], validations=[required_field_validator]
        )

        self.assertEqual(expected_yaml.strip(), actual_parsed_definition.content.strip())
        self.assertEqual(expected_parsed_definition.name, actual_parsed_definition.name)
        self.assertEqual(expected_parsed_definition.structure, actual_parsed_definition.structure)
        self.assertDictEqual(expected_parsed_definition.structure, actual_parsed_definition.structure)

    def test_create_schema_definition_with_validation(self):
        definition_name = "Test Name"
        validation_name = "Test Validation"
        description = "Test Description"

        expected_yaml = "\n".join(
            [
                "schema:",
                f"  name: {definition_name}",
                f"  description: {description}",
                "  fields: []",
                "  required: []",
                "  validation:",
                f"  - name: {validation_name}",
                "    arguments: []",
            ]
        )

        validation_entry = create_validation_entry(validation_name)
        parsed_definition = create_schema_definition(
            name=definition_name, description=description, validations=[validation_entry]
        )

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_enum_definition(self):
        enum_name = "Test Enum"
        enum_values = ["Value1", "Value2"]

        expected_yaml = "\n".join(
            [
                "enum:",
                f"  name: {enum_name}",
                "  values:",
                f"  - {enum_values[0]}",
                f"  - {enum_values[1]}",
            ]
        )

        parsed_definition = create_enum_definition(enum_name, enum_values)

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_usecase_definition(self):
        name = "Test Usecase"
        description = "Test Description"
        participant1_name = "Participant1 Name"
        participant1_description = "Participant1 Description"
        participant1_type = "Participant1 Type"
        participant1 = create_field_entry(participant1_name, participant1_type, participant1_description)
        step1_title = "Title 1"
        step1_source = "Source 1"
        step1_target = "Target 1"
        step1_action = "Action 1"
        step1 = create_step_entry(step1_title, step1_source, step1_target, step1_action)

        expected_yaml = "\n".join(
            [
                "usecase:",
                f"  name: {name}",
                f"  description: {description}",
                "  participants:",
                f"  - name: {participant1_name}",
                f"    type: {participant1_type}",
                f"    description: {participant1_description}",
                "  steps:",
                f"  - step: {step1_title}",
                f"    source: {step1_source}",
                f"    target: {step1_target}",
                f"    action: {step1_action}",
            ]
        )

        parsed_definition = create_usecase_definition(
            name, description=description, participants=[participant1], steps=[step1]
        )

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_model_definition(self):
        name = "Test Model"
        description = "Test Description"
        component1_name = "Component1 Name"
        component1_description = "Component1 Description"
        component1_type = "Component1 Type"
        component1 = create_field_entry(component1_name, component1_type, component1_description)

        expected_yaml = "\n".join(
            [
                "model:",
                f"  name: {name}",
                f"  description: {description}",
                "  components:",
                f"  - name: {component1_name}",
                f"    type: {component1_type}",
                f"    description: {component1_description}",
                "  behavior: []",
                "  state: []",
            ]
        )

        parsed_definition = create_model_definition(name, description=description, components=[component1])

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_schema_ext_definition(self):
        name = "Test Schema Extension"
        type = "Other Schema Type"
        description = "Some description content"
        schemaExt_name = "Ext1 Name"
        schemaExt_description = "Ext1 Description"
        schemaExt_type = "Ext1 Type"
        schemaExt = create_field_entry(schemaExt_name, schemaExt_type, schemaExt_description)

        expected_yaml = "\n".join(
            [
                "ext:",
                f"  name: {name}",
                f"  type: {type}",
                f"  description: {description}",
                "  schemaExt:",
                "    add:",
                f"    - name: {schemaExt_name}",
                f"      type: {schemaExt_type}",
                f"      description: {schemaExt_description}",
                "    required: []",
            ]
        )

        parsed_definition = create_schema_ext_definition(name, type=type, description=description, fields=[schemaExt])

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_enum_ext_definition(self):
        name = "Test Enum Extension"
        type = "Other Enum Type"
        description = "Some description content"
        value1 = "value1"

        expected_yaml = "\n".join(
            [
                "ext:",
                f"  name: {name}",
                f"  type: {type}",
                f"  description: {description}",
                "  enumExt:",
                "    add:",
                f"    - {value1}",
            ]
        )

        parsed_definition = create_enum_ext_definition(name, type=type, description=description, values=[value1])

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())
