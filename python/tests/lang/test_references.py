from unittest import TestCase

from aac.lang.references import get_definition_references_from_list

from tests.helpers.parsed_definitions import create_schema_definition, create_schema_ext_definition, create_field_entry, create_model_definition


class TestLangReferences(TestCase):

    def test_get_definition_references_from_list(self):
        source_definition_name = "Source Def"
        source_definition = create_schema_definition(source_definition_name)

        reference_definition1_name = "Reference Def 1"
        reference_definition1_component1 = create_field_entry("Component1", source_definition_name)
        reference_definition1 = create_model_definition(reference_definition1_name, components=[reference_definition1_component1])

        reference_definition2_name = "Reference Def 2"
        reference_definition1_component1 = create_field_entry("New Field", "NewFieldType")
        reference_definition2 = create_schema_ext_definition(reference_definition2_name, source_definition_name)

        unrelated_definition = "Unrelated Def"
        unrelated_definition_field = create_field_entry("Other Field", "OtherFieldType")
        unrelated_definition = create_schema_definition(unrelated_definition, fields=[unrelated_definition_field])

        expected_references = [reference_definition1, reference_definition2]
        definitions_to_search = expected_references + [unrelated_definition, source_definition]

        actual_references = get_definition_references_from_list(source_definition, definitions_to_search)

        self.assertCountEqual(actual_references, expected_references)
        self.assertListEqual(expected_references, actual_references)
