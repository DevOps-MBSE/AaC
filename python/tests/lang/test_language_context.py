from aac.lang.active_context_lifecycle_manager import get_active_context, get_initialized_language_context
from aac.lang.constants import (
    DEFINITION_FIELD_ADD,
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_EXTENSION_SCHEMA,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_REQUIRED,
    DEFINITION_FIELD_VALUES,
    DEFINITION_NAME_PRIMITIVES,
    PRIMITIVE_TYPE_STRING,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_MODEL,
    ROOT_KEY_SCHEMA,
)
from aac.lang.language_context import LanguageContext
from aac.lang.language_error import LanguageError
from aac.spec import get_aac_spec, get_primitives, get_root_keys

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
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
        test_definition_ext = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, self.TEST_SCHEMA_DEFINITION_NAME, fields=[ext_field, test_definition_field])

        test_enum = create_enum_definition(self.TEST_ENUM_DEFINITION_NAME, [self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        test_enum_ext_value = "extVal"
        # Adding self.ENUM_VALUE_EXAMPLE_ONE from the enum above to simulate extending an enum with a duplicate value
        test_enum_ext = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, self.TEST_ENUM_DEFINITION_NAME, values=[test_enum_ext_value, self.ENUM_VALUE_EXAMPLE_ONE])

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
        target_schema_definition_name = ROOT_KEY_MODEL
        target_enum_definition_name = DEFINITION_NAME_PRIMITIVES
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, target_schema_definition_name, fields=[schema_extension_field], required=[schema_extension_field_name])
        test_enum_extension = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, target_enum_definition_name, values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_values()
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [field.get(DEFINITION_FIELD_NAME) for field in extended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)

        language_context.remove_definitions_from_context([test_enum_extension, test_schema_extension])
        unextended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        unextended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        unextended_enum_values = unextended_enum_definition.get_values()
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_ONE, unextended_enum_values)
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, unextended_enum_values)

        unextended_schema_field_names = [field.get(DEFINITION_FIELD_NAME) for field in unextended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)]
        self.assertNotIn(schema_extension_field_name, unextended_schema_field_names)

    def test_update_extension_definition_in_context(self):
        target_schema_definition_name = ROOT_KEY_MODEL
        target_enum_definition_name = DEFINITION_NAME_PRIMITIVES
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, target_schema_definition_name, fields=[schema_extension_field], required=[schema_extension_field_name])
        test_enum_extension = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, target_enum_definition_name, values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_values()
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [field.get(DEFINITION_FIELD_NAME) for field in extended_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)

        # Remove self.ENUM_VALUE_EXAMPLE_TWO from the enum extension
        test_enum_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_ENUM][DEFINITION_FIELD_ADD].remove(self.ENUM_VALUE_EXAMPLE_TWO)

        # Add an additional field
        additional_schema_extension_field_name = "Additionalfield"
        additional_schema_extension_field = create_field_entry(additional_schema_extension_field_name, PRIMITIVE_TYPE_STRING)
        test_schema_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_SCHEMA][DEFINITION_FIELD_ADD].append(additional_schema_extension_field)
        test_schema_extension.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_SCHEMA][DEFINITION_FIELD_REQUIRED].append(additional_schema_extension_field_name)

        language_context.update_definitions_in_context([test_enum_extension, test_schema_extension])
        updated_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        updated_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        updated_enum_values = updated_enum_definition.get_values()
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, updated_enum_values)

        updated_schema_field_names = [field.get(DEFINITION_FIELD_NAME) for field in updated_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)]
        self.assertIn(additional_schema_extension_field_name, updated_schema_field_names)

    def test_get_primitives_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_primitives()
        actual_results = test_context.get_primitive_types()

        self.assertEqual(expected_results, actual_results)

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

        self.assertTrue(test_context.is_definition_type(ROOT_KEY_SCHEMA))
        self.assertFalse(test_context.is_definition_type("daaaaaaaaaata"))

    def test_get_root_keys(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_root_keys()
        actual_results = test_context.get_root_keys()

        self.assertEqual(expected_results, actual_results)

    def test_get_enum_definition_by_type_when_enum_is_in_core_spec(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        primitives_definition = test_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        behavior_type_definition = test_context.get_definition_by_name("BehaviorType")

        self.assertEqual(primitives_definition, test_context.get_enum_definition_by_type(PRIMITIVE_TYPE_STRING))
        self.assertEqual(behavior_type_definition, test_context.get_enum_definition_by_type("pub-sub"))

    def test_get_enum_definition_by_type_when_enum_is_added(self):
        test_context = LanguageContext()

        values = ["a", "b", "c"]

        [self.assertIsNone(test_context.get_enum_definition_by_type(value)) for value in values]

        enum = create_enum_definition("TestEnum", values)
        test_context.add_definition_to_context(enum)

        [self.assertEqual(enum, test_context.get_enum_definition_by_type(value)) for value in values]

    def test_language_error_if_apply_extension_with_duplicate_names(self):
        field1 = create_field_entry(f"{self.TEST_FIELD_DEFINITION_NAME}1")
        test_schema = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[field1])

        field2 = create_field_entry(f"{self.TEST_FIELD_DEFINITION_NAME}2")
        test_duplicate_schema = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[field2])

        language_context = LanguageContext([test_schema, test_duplicate_schema])

        self.assertEqual(len(language_context.definitions), 2)

        test_extension = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, self.TEST_SCHEMA_DEFINITION_NAME)

        with self.assertRaises(LanguageError) as cm:
            language_context.add_definition_to_context(test_extension)

        self.assertRegexpMatches(str(cm.exception).lower(), "duplicate.*definition.*name.*")
        self.assertIn(self.TEST_SCHEMA_DEFINITION_NAME, str(cm.exception))

    def test_uuid_in_active_context(self):
        definition_uuids_list = [definition.uid for definition in get_active_context().definitions]
        definition_uuids_set = set(definition_uuids_list)
        self.assertGreaterEqual(len(definition_uuids_set), len(get_aac_spec()))
        self.assertEqual(len(definition_uuids_list), len(definition_uuids_set))


class TestLanguageContextPluginInterface(ActiveContextTestCase):

    def test_language_context_activate_plugins(self):

        # Test that the active context initializes with expected active plugins
        active_context = get_active_context()
        # TODO adjust once we update the active context's default plugin strategy. # noqa: T101
        self.assertEqual(len(active_context.get_inactive_plugins()), 0)
        self.assertGreater(len(active_context.get_active_plugins()), 0)

        test_context = get_initialized_language_context(core_spec_only=True)
        initial_definitions_len = len(test_context.definitions)
        inactive_plugins = test_context.get_inactive_plugins()
        self.assertGreater(len(inactive_plugins), 2)
        self.assertEqual(len(test_context.get_active_plugins()), 0)

        plugin_to_activate = inactive_plugins.pop()
        test_context.activate_plugin(plugin_to_activate)
        self.assertEqual(len(test_context.get_active_plugins()), 1)
        self.assertEqual(test_context.get_active_plugins()[0].name, plugin_to_activate.name)

        test_context.activate_plugins(inactive_plugins)
        self.assertEqual(len(test_context.get_active_plugins()), len(inactive_plugins) + 1)  # Magic +1 for the popped plugin
        self.assertGreater(len(test_context.definitions), initial_definitions_len)

    def test_language_context_deactivate_plugins(self):

        # Test that the active context initializes with expected active plugins
        active_context = get_active_context()
        # TODO adjust once we update the active context's default plugin strategy. # noqa: T101
        self.assertEqual(len(active_context.get_inactive_plugins()), 0)
        self.assertGreater(len(active_context.get_active_plugins()), 0)

        test_context = get_initialized_language_context(core_spec_only=True)
        inactive_plugins = test_context.get_inactive_plugins()
        test_context.activate_plugins(inactive_plugins)
        initial_definitions_len = len(test_context.definitions)

        plugin_to_deactivate = inactive_plugins.pop()
        test_context.deactivate_plugin(plugin_to_deactivate)
        self.assertEqual(len(test_context.get_active_plugins()), len(inactive_plugins))
        self.assertNotIn(plugin_to_deactivate.name, [plugin.name for plugin in test_context.get_active_plugins()])

        test_context.deactivate_plugins(inactive_plugins)
        self.assertEqual(len(test_context.get_active_plugins()), 0)
        self.assertLess(len(test_context.definitions), initial_definitions_len)
