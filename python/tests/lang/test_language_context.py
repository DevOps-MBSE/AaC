from aac.io.parser import parse
from aac.io.files.aac_file import AaCFile
from aac.lang.active_context_lifecycle_manager import get_active_context, get_initialized_language_context
from aac.lang.constants import (
    BEHAVIOR_TYPE_PUBLISH_SUBSCRIBE,
    DEFINITION_FIELD_ADD,
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_EXTENSION_SCHEMA,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_REQUIRED,
    DEFINITION_FIELD_TYPE,
    DEFINITION_FIELD_VALUES,
    DEFINITION_NAME_BEHAVIOR_TYPE,
    DEFINITION_NAME_MODEL,
    DEFINITION_NAME_PRIMITIVES,
    DEFINITION_NAME_SCHEMA,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_STRING,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.language_context import LanguageContext
from aac.spec import get_aac_spec, get_primitives, get_root_keys

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.io import TemporaryTestFile, TemporaryAaCTestFile
from tests.helpers.parsed_definitions import (
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
    create_schema_definition,
    create_schema_ext_definition,
)
from tests.helpers.prebuilt_definition_constants import (
    TEST_DOCUMENT_CONTENT,
    TEST_SCHEMA_A,
    TEST_SCHEMA_B,
    TEST_SERVICE_ONE,
    TEST_SERVICE_TWO,
)


class TestLanguageContext(ActiveContextTestCase):

    ENUM_VALUE_EXAMPLE_ONE = "valueOne"
    ENUM_VALUE_EXAMPLE_TWO = "valueTwo"
    TEST_FIELD_DEFINITION_NAME = "TestField"
    TEST_SCHEMA_DEFINITION_NAME = "TestSchema"
    TEST_ENUM_DEFINITION_NAME = "TestEnum"
    TEST_SCHEMA_EXT_DEFINITION_NAME = "TestSchemaExtension"
    TEST_ENUM_EXT_DEFINITION_NAME = "TestEnumExtension"

    def test_add_definitions_to_context_with_extensions(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, PRIMITIVE_TYPE_STRING)
        test_definition = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[test_definition_field])

        schema_ext_field_name = "extField"
        schema_ext_field_type = "ExtField"
        ext_field = create_field_entry(schema_ext_field_name, schema_ext_field_type)
        # Adding test_definition_field from the data definition above to simulate extending a definition with a duplicate value
        test_definition_ext = create_schema_ext_definition(
            self.TEST_SCHEMA_EXT_DEFINITION_NAME, self.TEST_SCHEMA_DEFINITION_NAME, fields=[ext_field, test_definition_field]
        )

        test_enum = create_enum_definition(
            self.TEST_ENUM_DEFINITION_NAME, [self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO]
        )

        test_enum_ext_value = "extVal"
        # Adding self.ENUM_VALUE_EXAMPLE_ONE from the enum above to simulate extending an enum with a duplicate value
        test_enum_ext = create_enum_ext_definition(
            self.TEST_ENUM_EXT_DEFINITION_NAME,
            self.TEST_ENUM_DEFINITION_NAME,
            values=[test_enum_ext_value, self.ENUM_VALUE_EXAMPLE_ONE],
        )

        language_context = LanguageContext()
        self.assertEqual(0, len(language_context.definitions))

        language_context.add_definitions_to_context([test_definition, test_enum])
        self.assertEqual(2, len(language_context.definitions))

        self.assertIn(test_definition, language_context.definitions)
        self.assertIn(test_enum, language_context.definitions)

        # Assert pre-extension state
        self.assertEqual(1, len(test_definition.structure[ROOT_KEY_SCHEMA][DEFINITION_FIELD_FIELDS]))
        self.assertEqual(2, len(test_enum.structure[ROOT_KEY_ENUM][DEFINITION_FIELD_VALUES]))

        # Assert post-extension state
        language_context.add_definitions_to_context([test_definition_ext, test_enum_ext])
        context_modified_test_definition = language_context.get_definition_by_name(self.TEST_SCHEMA_DEFINITION_NAME)
        self.assertEqual(2, len(context_modified_test_definition.structure[ROOT_KEY_SCHEMA][DEFINITION_FIELD_FIELDS]))
        self.assertIn(schema_ext_field_name, context_modified_test_definition.to_yaml())
        self.assertIn(schema_ext_field_type, context_modified_test_definition.to_yaml())

        context_modified_test_enum = language_context.get_definition_by_name(self.TEST_ENUM_DEFINITION_NAME)
        self.assertEqual(3, len(context_modified_test_enum.structure[ROOT_KEY_ENUM][DEFINITION_FIELD_VALUES]))
        self.assertIn(test_enum_ext_value, context_modified_test_enum.to_yaml())

    def test_remove_definitions_from_context(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, PRIMITIVE_TYPE_STRING)
        test_definition_one = create_schema_definition("Test1", fields=[test_definition_field])
        test_definition_two = create_schema_definition("Test2", fields=[test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        core_spec_definition_count = len(language_context.definitions)

        language_context.add_definitions_to_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count + 2, len(language_context.definitions))

        language_context.remove_definitions_from_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count, len(language_context.definitions))

    def test_update_definition_in_context(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, PRIMITIVE_TYPE_STRING)
        test_definition = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definition_to_context(test_definition)

        original_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, original_context_definition.structure)

        test_definition.structure[ROOT_KEY_SCHEMA][DEFINITION_FIELD_FIELDS][0][DEFINITION_FIELD_NAME] = "NewTestField"
        language_context.update_definition_in_context(test_definition)

        altered_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, altered_context_definition.structure)
        self.assertNotEqual(original_context_definition.structure, altered_context_definition.structure)

    def test_remove_extension_definition_from_context(self):
        target_schema_definition_name = DEFINITION_NAME_MODEL
        target_enum_definition_name = DEFINITION_NAME_PRIMITIVES
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension = create_schema_ext_definition(
            self.TEST_SCHEMA_EXT_DEFINITION_NAME,
            target_schema_definition_name,
            fields=[schema_extension_field],
            required=[schema_extension_field_name],
        )
        test_enum_extension = create_enum_ext_definition(
            self.TEST_ENUM_EXT_DEFINITION_NAME,
            target_enum_definition_name,
            values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO],
        )

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_values()
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [
            field.get(DEFINITION_FIELD_NAME)
            for field in extended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        ]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)

        language_context.remove_definitions_from_context([test_enum_extension, test_schema_extension])
        unextended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        unextended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        unextended_enum_values = unextended_enum_definition.get_values()
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_ONE, unextended_enum_values)
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, unextended_enum_values)

        unextended_schema_field_names = [
            field.get(DEFINITION_FIELD_NAME)
            for field in unextended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        ]
        self.assertNotIn(schema_extension_field_name, unextended_schema_field_names)

    def test_update_extension_definition_in_context(self):
        target_schema_definition_name = DEFINITION_NAME_MODEL
        target_enum_definition_name = DEFINITION_NAME_PRIMITIVES
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension = create_schema_ext_definition(
            self.TEST_SCHEMA_EXT_DEFINITION_NAME,
            target_schema_definition_name,
            fields=[schema_extension_field],
            required=[schema_extension_field_name],
        )
        test_enum_extension = create_enum_ext_definition(
            self.TEST_ENUM_EXT_DEFINITION_NAME,
            target_enum_definition_name,
            values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO],
        )

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_values()
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [
            field.get(DEFINITION_FIELD_NAME)
            for field in extended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        ]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)

        # Remove self.ENUM_VALUE_EXAMPLE_TWO from the enum extension
        test_enum_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_ENUM][DEFINITION_FIELD_ADD].remove(
            self.ENUM_VALUE_EXAMPLE_TWO
        )

        # Add an additional field
        additional_schema_extension_field_name = "Additionalfield"
        additional_schema_extension_field = create_field_entry(additional_schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_SCHEMA][DEFINITION_FIELD_ADD].append(
            additional_schema_extension_field
        )
        test_schema_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_SCHEMA][
            DEFINITION_FIELD_REQUIRED
        ].append(additional_schema_extension_field_name)

        language_context.update_definitions_in_context([test_enum_extension, test_schema_extension])
        updated_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        updated_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        updated_enum_values = updated_enum_definition.get_values()
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, updated_enum_values)

        updated_schema_field_names = [
            field.get(DEFINITION_FIELD_NAME)
            for field in updated_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        ]
        self.assertIn(additional_schema_extension_field_name, updated_schema_field_names)

    def test_get_primitives_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_primitives()
        actual_results = test_context.get_primitive_types()

        self.assertCountEqual(expected_results, actual_results)

    def test_get_defined_types_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        actual_results = test_context.get_defined_types()
        expected_results = [definition.name for definition in test_context.definitions]

        self.assertListEqual(expected_results, actual_results)

    def test_is_primitive(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        self.assertTrue(test_context.is_primitive_type(PRIMITIVE_TYPE_STRING))
        self.assertFalse(test_context.is_primitive_type("striiiiiiiiiiiiiiing"))

    def test_is_defined_type(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        self.assertTrue(test_context.is_definition_type(DEFINITION_NAME_SCHEMA))
        self.assertFalse(test_context.is_definition_type("daaaaaaaaaata"))

    def test_get_root_keys(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_root_keys()
        actual_results = test_context.get_root_keys()

        self.assertCountEqual(expected_results, actual_results)

    def test_get_root_definitions(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        actual_results = test_context.get_root_definitions()
        expected_root_type_names = ['Import', 'Enum', 'Extension', 'Validation', 'Schema', 'Model', 'Usecase', 'CommandGroup', 'Plugin', 'Specification']
        self.assertListEqual(sorted([definition.name for definition in actual_results]), sorted(expected_root_type_names))

    def test_get_enum_definition_by_type_when_enum_is_in_core_spec(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        primitives_definition = test_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        behavior_type_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR_TYPE)

        self.assertEqual(primitives_definition, test_context.get_enum_definition_by_type(PRIMITIVE_TYPE_STRING))
        self.assertEqual(behavior_type_definition, test_context.get_enum_definition_by_type(BEHAVIOR_TYPE_PUBLISH_SUBSCRIBE))

    def test_get_enum_definition_by_type_when_enum_is_added(self):
        test_context = LanguageContext()

        values = ["a", "b", "c"]

        [self.assertIsNone(test_context.get_enum_definition_by_type(value)) for value in values]

        enum = create_enum_definition("TestEnum", values)
        test_context.add_definition_to_context(enum)

        [self.assertEqual(enum, test_context.get_enum_definition_by_type(value)) for value in values]

    def test_uuid_in_active_context(self):
        definition_uuids_list = [definition.uid for definition in get_active_context().definitions]
        definition_uuids_set = set(definition_uuids_list)
        self.assertGreaterEqual(len(definition_uuids_set), len(get_aac_spec()))
        self.assertEqual(len(definition_uuids_list), len(definition_uuids_set))

    def test_language_context_loads_state_from_file(self):
        test_definition = create_schema_definition("TestDefinition")
        with TemporaryAaCTestFile(test_definition.to_yaml()) as test_definition_file:
            test_definition.source = AaCFile(test_definition_file.name, True, True)

            test_context = get_active_context()
            test_context.add_definition_to_context(test_definition)

            with TemporaryTestFile("") as state_file:
                test_context.export_to_file(state_file.name)

                new_context = LanguageContext()
                new_context.import_from_file(state_file.name)

                imported_plugins = {plugin.name for plugin in new_context.get_active_plugins()}
                exported_plugins = {plugin.name for plugin in test_context.get_active_plugins()}
                self.assertSetEqual(imported_plugins, exported_plugins)

    def test_language_context_editable_files(self):
        active_context = get_active_context()

        primitive_definition = active_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        active_context.remove_definition_from_context(primitive_definition)

        self.assertIsNotNone(active_context.get_definition_by_name(primitive_definition.name))

        new_enum_value = "test_primitive"
        updated_primitive_definition = primitive_definition.copy()
        updated_primitive_definition.structure[primitive_definition.get_root_key()][DEFINITION_FIELD_VALUES].append(
            new_enum_value
        )
        active_context.update_definition_in_context(primitive_definition)

        actual_primitive_definition = active_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        self.assertEqual(primitive_definition, actual_primitive_definition)
        self.assertNotEqual(primitive_definition, updated_primitive_definition)

    def test_language_context_copy(self):
        definition_to_add = create_schema_definition("TestAdd", fields=[create_field_entry("field", PRIMITIVE_TYPE_STRING)])
        definition_to_remove = create_schema_definition(
            "TestRemove", fields=[create_field_entry("field", PRIMITIVE_TYPE_STRING)]
        )

        # Add the definition to test removing to the original context
        original_context = get_active_context()
        original_context.add_definition_to_context(definition_to_remove)

        # Add the additional definition to the context copy
        copy_context = original_context.copy()
        copy_context.add_definition_to_context(definition_to_add)

        # Assert that the additional definition is not in the original context
        self.assertIsNone(original_context.get_definition_by_name(definition_to_add.name))
        self.assertIsNotNone(copy_context.get_definition_by_name(definition_to_add.name))

        # Demonstrate that removing a definition from the original doesn't affect the copy
        original_context.remove_definition_from_context(definition_to_remove)

        # Assert the removed definition isn't removed from the copy context
        self.assertIsNone(original_context.get_definition_by_name(definition_to_remove.name))
        self.assertIsNotNone(copy_context.get_definition_by_name(definition_to_remove.name))

        # Assert that the copy context has the additional definition and the definition removed from the original context (+2 definitions in copy context len)
        self.assertEqual(len(original_context.definitions), len(copy_context.definitions) - 2)


class TestLanguageContextPluginInterface(ActiveContextTestCase):
    def test_language_context_activate_plugins(self):
        # Test that the active context initializes with expected active plugins
        test_context = get_active_context()
        # TODO adjust once we update the active context's default plugin strategy. # noqa: T101
        self.assertEqual(len(test_context.get_inactive_plugins()), 0)
        self.assertGreater(len(test_context.get_active_plugins()), 0)

        test_context = get_initialized_language_context(core_spec_only=True)
        initial_definitions_len = len(test_context.definitions)
        inactive_plugins = test_context.get_inactive_plugins()
        self.assertGreater(len(inactive_plugins), 2)
        self.assertEqual(len(test_context.get_active_plugins()), 0)

        first_plugin_to_activate = inactive_plugins.pop()
        test_context.activate_plugin(first_plugin_to_activate)
        self.assertEqual(len(test_context.get_active_plugins()), 1)
        self.assertEqual(test_context.get_active_plugins()[0].name, first_plugin_to_activate.name)

        second_plugin_to_activate = inactive_plugins.pop()
        test_context.activate_plugin_by_name(second_plugin_to_activate.name)
        self.assertEqual(len(test_context.get_active_plugins()), 2)
        self.assertEqual(test_context.get_active_plugins()[1].name, second_plugin_to_activate.name)

        test_context.activate_plugins(inactive_plugins)
        self.assertEqual(len(test_context.get_active_plugins()), len(inactive_plugins) + 2)  # Magic +2 for the popped plugins
        self.assertGreater(len(test_context.definitions), initial_definitions_len)

    def test_language_context_deactivate_plugins(self):
        # Test that the active context initializes with expected active plugins
        test_context = get_active_context()
        # TODO adjust once we update the active context's default plugin strategy. # noqa: T101
        self.assertEqual(len(test_context.get_inactive_plugins()), 0)
        self.assertGreater(len(test_context.get_active_plugins()), 0)

        test_context = get_initialized_language_context(core_spec_only=True)
        inactive_plugins = test_context.get_inactive_plugins()
        test_context.activate_plugins(inactive_plugins)
        initial_definitions_len = len(test_context.definitions)

        first_plugin_to_deactivate = inactive_plugins.pop()
        test_context.deactivate_plugin(first_plugin_to_deactivate)
        self.assertEqual(len(test_context.get_active_plugins()), len(inactive_plugins))
        self.assertNotIn(first_plugin_to_deactivate.name, [plugin.name for plugin in test_context.get_active_plugins()])

        second_plugin_to_deactivate = inactive_plugins.pop()
        test_context.deactivate_plugin(second_plugin_to_deactivate)
        self.assertEqual(len(test_context.get_active_plugins()), len(inactive_plugins))
        self.assertNotIn(second_plugin_to_deactivate.name, [plugin.name for plugin in test_context.get_active_plugins()])

        test_context.deactivate_plugins(inactive_plugins)
        self.assertEqual(len(test_context.get_active_plugins()), 0)
        self.assertLess(len(test_context.definitions), initial_definitions_len)

    def test_language_context_activate_deactivate_missing_plugins(self):
        # Test that the active context initializes with expected active plugins
        test_context = get_active_context()
        initial_plugins_count = len(test_context.plugins)

        invalid_plugin_name = "IDontExist"
        test_context.activate_plugin_by_name(invalid_plugin_name)
        self.assertEqual(initial_plugins_count, len(test_context.get_active_plugins()))

        invalid_plugin_name = "IDontExist"
        test_context.deactivate_plugin_by_name(invalid_plugin_name)
        self.assertEqual(initial_plugins_count, len(test_context.get_active_plugins()))


class TestLanguageContextGetDefinitionMethods(ActiveContextTestCase):
    def test_language_context_get_definitions_by_name(self):
        test_context = get_active_context()

        with TemporaryAaCTestFile(TEST_DOCUMENT_CONTENT) as test_file:
            test_content_definitions = parse(test_file.name)
            test_context.add_definitions_to_context(test_content_definitions)

        self.assertIn(test_file.name, [file.uri for file in test_context.get_files_in_context()])
        self.assertIn(TEST_SCHEMA_A.name, test_context.get_defined_types())
        self.assertIn(TEST_SCHEMA_B.name, test_context.get_defined_types())
        self.assertIn(TEST_SERVICE_ONE.name, test_context.get_defined_types())

    def test_language_context_get_definitions_by_file_uri(self):
        test_context = get_active_context()

        with TemporaryAaCTestFile(TEST_DOCUMENT_CONTENT) as test_file:
            test_content_definitions = parse(test_file.name)
            test_context.add_definitions_to_context(test_content_definitions)

        actual_definitions = test_context.get_definitions_by_file_uri(test_file.name)
        parsed_schema_a, *_ = [definition for definition in test_content_definitions if definition.name == TEST_SCHEMA_A.name]
        parsed_schema_b, *_ = [definition for definition in test_content_definitions if definition.name == TEST_SCHEMA_B.name]
        parsed_service_one, *_ = [
            definition for definition in test_content_definitions if definition.name == TEST_SERVICE_ONE.name
        ]
        self.assertIn(parsed_schema_a, actual_definitions)
        self.assertIn(parsed_schema_b, actual_definitions)
        self.assertIn(parsed_service_one, actual_definitions)


class TestLanguageContextFileMethods(ActiveContextTestCase):
    def test_language_context_write_file(self):
        test_context = get_active_context()

        with TemporaryAaCTestFile(TEST_DOCUMENT_CONTENT) as test_file:
            test_content_definitions = parse(test_file.name)
            test_context.add_definitions_to_context(test_content_definitions)

            # Assert test content is in the context
            schema_a_definition = test_context.get_definition_by_name(TEST_SCHEMA_A.name)
            schema_b_definition = test_context.get_definition_by_name(TEST_SCHEMA_B.name)
            service_one_definition = test_context.get_definition_by_name(TEST_SERVICE_ONE.name)

            self.assertEqual(3, len(test_content_definitions))
            self.assertIsNotNone(schema_a_definition)
            self.assertIsNotNone(schema_b_definition)
            self.assertIsNotNone(service_one_definition)

            # Update Schema A with a new field
            schema_a_updated_field = create_field_entry("new_field", PRIMITIVE_TYPE_STRING)
            schema_a_definition.get_fields().append(schema_a_updated_field)
            test_context.update_definition_in_context(schema_a_definition)

            # Update Schema B field type
            schema_b_definition.get_fields()[0][DEFINITION_FIELD_TYPE] = PRIMITIVE_TYPE_DATE
            test_context.update_definition_in_context(schema_a_definition)

            # Remove Service One
            test_context.remove_definition_from_context(service_one_definition)

            # Add Service Two
            service_two_definition = TEST_SERVICE_TWO.copy()
            service_two_definition.source.uri = test_file.name
            test_context.add_definition_to_context(service_two_definition)

            # Write changes to file
            test_context.update_architecture_file(test_file.name)

            # Re-read file and assert changes are as expected.
            updated_definitions = parse(test_file.name)
            updated_schema_a_definition = get_definition_by_name(TEST_SCHEMA_A.name, updated_definitions)
            updated_schema_b_definition = get_definition_by_name(TEST_SCHEMA_B.name, updated_definitions)
            updated_service_one_definition = get_definition_by_name(TEST_SERVICE_ONE.name, updated_definitions)
            updated_service_two_definition = get_definition_by_name(TEST_SERVICE_TWO.name, updated_definitions)

            self.assertIsNotNone(updated_schema_a_definition)
            self.assertIsNotNone(updated_schema_b_definition)
            self.assertIsNone(updated_service_one_definition)
            self.assertIsNotNone(updated_service_two_definition)

            self.assertIn(schema_a_updated_field, updated_schema_a_definition.get_fields())
            self.assertEqual(PRIMITIVE_TYPE_DATE, updated_schema_b_definition.get_fields()[0].get(DEFINITION_FIELD_TYPE))

            # Assert Definition Order is Kept
            self.assertEqual(3, len(updated_definitions))
            self.assertEqual(updated_definitions[0].name, test_content_definitions[0].name)
            self.assertEqual(updated_definitions[1].name, test_content_definitions[1].name)
            self.assertEqual(updated_definitions[2].name, updated_service_two_definition.name)
