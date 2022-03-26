
"""
Unit tests for the testing helper parsed_definitions module.
"""

from unittest import TestCase

from aac.parser import parse

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_data_ext_definition,
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

    def test_create_data_definition_without_fields_or_required(self):
        data_name = "Test Name"

        expected_yaml = "\n".join(
            [
                "data:",
                f"  name: {data_name}",
                "  fields: []",
                "  required: []",
                "  validation: []",
            ]
        )

        parsed_definition = create_data_definition(name=data_name)

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_data_definition_with_fields_and_required(self):
        data_name = "Test Name"
        field1_name = "field1"
        field1_description = "description for field 1"
        field1_type = "Type1"

        expected_yaml = "\n".join(
            [
                "data:",
                f"  name: {data_name}",
                "  fields:",
                f"  - name: {field1_name}",
                f"    type: {field1_type}",
                f"    description: {field1_description}",
                "  required:",
                f"  - {field1_name}",
                "  validation: []",
            ]
        )

        field1_definition = create_field_entry(field1_name, field1_type, field1_description)

        expected_parsed_definition = parse(expected_yaml)[0]
        actual_parsed_definition = create_data_definition(name=data_name, fields=[field1_definition], required=[field1_name])

        self.assertEqual(expected_yaml.strip(), actual_parsed_definition.content.strip())
        self.assertEqual(expected_parsed_definition.name, actual_parsed_definition.name)
        self.assertEqual(expected_parsed_definition.definition, actual_parsed_definition.definition)
        self.assertDictEqual(expected_parsed_definition.definition, actual_parsed_definition.definition)

    def test_create_data_definition_with_validation(self):
        data_name = "Test Name"
        validation_name = "Test Validation"

        expected_yaml = "\n".join(
            [
                "data:",
                f"  name: {data_name}",
                "  fields: []",
                "  required: []",
                "  validation:",
                f"  - name: {validation_name}",
                "    arguments: []"
            ]
        )

        validation_entry = create_validation_entry(validation_name)
        parsed_definition = create_data_definition(name=data_name, validation=[validation_entry])

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

    def test_create_data_ext_definition(self):
        name = "Test Data Extension"
        type = "Other Data Type"
        dataExt1_name = "Ext1 Name"
        dataExt1_description = "Ext1 Description"
        dataExt1_type = "Ext1 Type"
        dataExt1 = create_field_entry(dataExt1_name, dataExt1_type, dataExt1_description)

        expected_yaml = "\n".join(
            [
                "ext:",
                f"  name: {name}",
                f"  type: {type}",
                "  dataExt:",
                "    add:",
                f"    - name: {dataExt1_name}",
                f"      type: {dataExt1_type}",
                f"      description: {dataExt1_description}",
                "    required: []",
            ]
        )

        parsed_definition = create_data_ext_definition(name, type=type, fields=[dataExt1])

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())

    def test_create_enum_ext_definition(self):
        name = "Test Enum Extension"
        type = "Other Enum Type"
        value1 = "value1"

        expected_yaml = "\n".join(
            [
                "ext:",
                f"  name: {name}",
                f"  type: {type}",
                "  enumExt:",
                "    add:",
                f"    - {value1}",
            ]
        )

        parsed_definition = create_enum_ext_definition(name, type=type, values=[value1])

        self.assertEqual(expected_yaml.strip(), parsed_definition.content.strip())
