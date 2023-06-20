import os
from aac.io.parser import parse
from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_COMPONENTS, DEFINITION_FIELD_TYPE, ROOT_KEY_MODEL
from aac.plugins.first_party.sysml.constants import (
    SYSML_DEFINITION_FIELD_BLOCKS,
    SYSML_DEFINITION_FIELD_SYSML_ELEMENT,
    SYSML_DEFINITION_NAME_BDD,
    SYSML_DEFINITION_NAME_BLOCK,
    SYSML_ROOT_KEY_BDD,
    SYSML_ROOT_KEY_BLOCK,
)

from aac.plugins.first_party.sysml.sysml_definition_builder import create_block, create_block_definition_diagram
from aac.plugins.first_party.sysml.sysml_impl import (
    GENERATED_FILE_SUFFIX_CORE,
    GENERATED_FILE_SUFFIX_SYSML,
    _convert_aac_core_definition_to_sysml_definition,
    _convert_sysml_definition_to_aac_core_definition,
    aac_to_sysml,
    sysml_to_aac,
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.io import temporary_test_file
from tests.helpers.parsed_definitions import create_field_entry, create_model_definition


class TestSysmlPlugin(ActiveContextTestCase):
    def test_sysml_to_aac_command(self):
        sysml_test_definitions = [TEST_BLOCK_DEFINITION, TEST_NAMESPACE_BLOCK_DEFINITION, TEST_BLOCK_DEFINITION_DIAGRAM]
        sysml_test_definitions_content = [definition.to_yaml() for definition in sysml_test_definitions]
        test_file_content = DEFINITION_SEPARATOR.join(sysml_test_definitions_content)

        with temporary_test_file(test_file_content) as arch_file:
            output_directory = os.path.dirname(arch_file.name)

            file_name, file_ext = os.path.splitext(arch_file.name)
            expected_output_file_name = f"{file_name}_{GENERATED_FILE_SUFFIX_CORE}{file_ext}"
            expected_output_file_path = os.path.join(output_directory, expected_output_file_name)
            result = sysml_to_aac(arch_file.name, output_directory)

            self.assertTrue(result.is_success())
            self.assertTrue(os.path.isfile(expected_output_file_path))

            actual_models = parse(expected_output_file_path)
            self.assertEqual(3, len(actual_models))

            actual_block_model = actual_models[0]
            self.assertEqual(TEST_BLOCK_DEFINITION.name, actual_block_model.name)

            actual_namespace_block_model = actual_models[1]
            self.assertEqual(TEST_NAMESPACE_BLOCK_DEFINITION.name, actual_namespace_block_model.name)

            actual_block_diagram_model = actual_models[2]
            self.assertEqual(TEST_BLOCK_DEFINITION_DIAGRAM.name, actual_block_diagram_model.name)
            components_fields = actual_block_diagram_model.get_top_level_fields().get(DEFINITION_FIELD_COMPONENTS, {})
            components_field_types = [field.get(DEFINITION_FIELD_TYPE) for field in components_fields]
            self.assertIn(actual_block_model.name, components_field_types)

    def test_aac_to_sysml_command(self):
        test_file_content = (
            f"{TEST_BLOCK_MODEL_DEFINITION.to_yaml()}{DEFINITION_SEPARATOR}{TEST_BLOCK_DIAGRAM_MODEL_DEFINITION.to_yaml()}"
        )

        with temporary_test_file(test_file_content) as arch_file:
            output_directory = os.path.dirname(arch_file.name)

            file_name, file_ext = os.path.splitext(arch_file.name)
            expected_output_file_name = f"{file_name}_{GENERATED_FILE_SUFFIX_SYSML}{file_ext}"
            expected_output_file_path = os.path.join(output_directory, expected_output_file_name)
            result = aac_to_sysml(arch_file.name, output_directory)

            self.assertTrue(result.is_success())
            self.assertTrue(os.path.isfile(expected_output_file_path))

            actual_models = parse(expected_output_file_path)
            self.assertEqual(2, len(actual_models))

            actual_block_model = actual_models[0]
            self.assertEqual(TEST_BLOCK_DEFINITION.name, actual_block_model.name)

            actual_block_diagram_model = actual_models[1]
            self.assertEqual(TEST_BLOCK_DEFINITION_DIAGRAM.name, actual_block_diagram_model.name)
            diagram_blocks_field = actual_block_diagram_model.get_top_level_fields().get(SYSML_DEFINITION_FIELD_BLOCKS, [])
            self.assertIn(actual_block_model.name, diagram_blocks_field)


class TestSysmlConversion(ActiveContextTestCase):
    def test_sysml_bdd_to_aac(self):
        test_context = get_active_context()
        test_block = TEST_BLOCK_DEFINITION.copy()
        test_bdd = TEST_BLOCK_DEFINITION_DIAGRAM.copy()

        actual_bdd_model = _convert_sysml_definition_to_aac_core_definition(test_bdd, test_context)
        self.assertEqual(ROOT_KEY_MODEL, actual_bdd_model.get_root_key())
        self.assertEqual(test_bdd.name, actual_bdd_model.name)

        actual_block_model = _convert_sysml_definition_to_aac_core_definition(test_block, test_context)
        self.assertEqual(ROOT_KEY_MODEL, actual_block_model.get_root_key())
        self.assertEqual(test_block.name, actual_block_model.name)

    def test_aac_to_sysml_bdd(self):
        test_context = get_active_context()
        test_block_model = TEST_BLOCK_MODEL_DEFINITION.copy()
        test_bdd_model = TEST_BLOCK_DIAGRAM_MODEL_DEFINITION.copy()

        actual_bdd = _convert_aac_core_definition_to_sysml_definition(test_bdd_model, test_context)
        self.assertEqual(SYSML_ROOT_KEY_BDD, actual_bdd.get_root_key())
        self.assertEqual(test_bdd_model.name, actual_bdd.name)

        actual_block = _convert_aac_core_definition_to_sysml_definition(test_block_model, test_context)
        self.assertEqual(SYSML_ROOT_KEY_BLOCK, actual_block.get_root_key())
        self.assertEqual(test_block_model.name, actual_block.name)


# Plugin-specific testing constants
TEST_BLOCK_DEFINITION_NAME = "TestBlock"
TEST_BLOCK_DEFINITION = create_block(TEST_BLOCK_DEFINITION_NAME)

TEST_NAMESPACE = "TestNamespace"
TEST_NAMESPACE_BLOCK_DEFINITION = create_block(TEST_NAMESPACE)

TEST_BLOCK_DEFINITION_DIAGRAM_NAME = "TestBlockDiagram"
TEST_BLOCK_DEFINITION_DIAGRAM = create_block_definition_diagram(
    TEST_BLOCK_DEFINITION_DIAGRAM_NAME, TEST_NAMESPACE, [TEST_BLOCK_DEFINITION_NAME]
)

TEST_BLOCK_MODEL_DEFINITION = create_model_definition(TEST_BLOCK_DEFINITION_NAME)
TEST_BLOCK_DIAGRAM_MODEL_COMPONENTS_FIELD = create_field_entry(TEST_BLOCK_DEFINITION_NAME.lower(), TEST_BLOCK_DEFINITION_NAME)
TEST_BLOCK_DIAGRAM_MODEL_DEFINITION = create_model_definition(
    TEST_BLOCK_DEFINITION_DIAGRAM_NAME, components=[TEST_BLOCK_DIAGRAM_MODEL_COMPONENTS_FIELD]
)

# Add Model Metadata
diagram_top_fields = TEST_BLOCK_DIAGRAM_MODEL_DEFINITION.structure.get(TEST_BLOCK_DIAGRAM_MODEL_DEFINITION.get_root_key(), {})
diagram_top_fields[SYSML_DEFINITION_FIELD_SYSML_ELEMENT] = SYSML_DEFINITION_NAME_BDD

diagram_top_fields = TEST_BLOCK_MODEL_DEFINITION.structure.get(TEST_BLOCK_MODEL_DEFINITION.get_root_key(), {})
diagram_top_fields[SYSML_DEFINITION_FIELD_SYSML_ELEMENT] = SYSML_DEFINITION_NAME_BLOCK
