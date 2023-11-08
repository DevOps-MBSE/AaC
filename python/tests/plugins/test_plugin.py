from unittest.case import TestCase

from aac.validate import validated_definitions, ValidationError
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_TYPE, DEFINITION_NAME_PRIMITIVES, PRIMITIVE_TYPE_STRING
from aac.plugins.plugin import Plugin
from aac.plugins.plugin_manager import clear_plugins, register_plugin
from tests.active_context_test_case import ActiveContextTestCase

from tests.helpers.contribution_points import assert_items_are_registered, create_command, create_validation
from tests.helpers.parsed_definitions import create_enum_ext_definition, create_field_entry, create_schema_definition, create_validation_definition


class TestPlugin(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plugin = Plugin("test")

    def test_register_items(self):
        commands = {create_command("Test")}
        assert_items_are_registered(self, commands, self.plugin.register_commands, self.plugin.get_commands)

        validations = {create_validation("Test", create_validation_definition("validation"))}
        assert_items_are_registered(self, validations, self.plugin.register_definition_validations, self.plugin.get_definition_validations)

        definitions = {create_schema_definition("Test")}
        assert_items_are_registered(self, definitions, self.plugin.register_definitions, self.plugin.get_definitions)


class TestInterPluginReferences(ActiveContextTestCase):
    """A test suite dedicated to testing interactions between plugins."""

    def setUp(self) -> None:
        super().setUp()

        self.plugin_a = Plugin("TestPluginA")
        self.plugin_b = Plugin("TestPluginB")

    def tearDown(self) -> None:
        super().tearDown()
        # Since these tests manually register plugins, clear out the plugin manager on cleanup
        clear_plugins()

    def test_cross_plugin_definition_reference(self):
        """Demonstrates that a plugin can reference definitions from another plugin and pass validation."""

        # Plugin A Definitions
        plugin_a_field_string = create_field_entry("string_field", PRIMITIVE_TYPE_STRING)
        plugin_a_schema_fields = [plugin_a_field_string]
        plugin_a_schema_definition = create_schema_definition("schemaA", fields=plugin_a_schema_fields)
        self.plugin_a.register_definitions([plugin_a_schema_definition])

        # Plugin B Definitions
        plugin_b_schema_field = create_field_entry("plugin_a_field", plugin_a_schema_definition.name)
        plugin_b_schema_fields = [plugin_b_schema_field]
        plugin_b_schema_definition = create_schema_definition("schemaB", fields=plugin_b_schema_fields)
        self.plugin_b.register_definitions([plugin_b_schema_definition])

        # Assert that plugin b fails validation when plugin a is not present.
        register_plugin(self.plugin_b)

        active_context = get_active_context(reload_context=True)
        context_sourced_plugin_a_definition = active_context.get_definition_by_name(plugin_a_schema_definition.name)
        context_sourced_plugin_b_definition = active_context.get_definition_by_name(plugin_b_schema_definition.name)

        self.assertIsNone(context_sourced_plugin_a_definition)
        self.assertIsNotNone(context_sourced_plugin_b_definition)

        # Assert that the field in plugin b's definition sourced from plugin a is present.
        plugin_b_field_referencing_plugin_a, *_ = context_sourced_plugin_b_definition.get_fields()
        self.assertIsNotNone(plugin_b_field_referencing_plugin_a)
        self.assertEqual(plugin_a_schema_definition.name, plugin_b_field_referencing_plugin_a.get(DEFINITION_FIELD_TYPE))

        # Perform validation on the definitions to demonstrate that plugin b is invalid.
        with self.assertRaises(ValidationError) as error:
            with validated_definitions([]):
                pass

            exception = error.exception
            self.assertEqual(ValidationError, type(exception))
            self.assertEqual(len(exception.args), 1)
            self.assertIn("undefined", exception.args[0].lower())

        # Assert that the plugin validation passes when both plugins are active.
        register_plugin(self.plugin_a)

        active_context = get_active_context(reload_context=True)
        context_sourced_plugin_a_definition = active_context.get_definition_by_name(plugin_a_schema_definition.name)
        context_sourced_plugin_b_definition = active_context.get_definition_by_name(plugin_b_schema_definition.name)

        self.assertIsNotNone(context_sourced_plugin_a_definition)
        self.assertIsNotNone(context_sourced_plugin_b_definition)

        # Perform validation on the definitions to demonstrate that they're valid.
        actual_result = None
        with validated_definitions([]) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_cross_plugin_definition_reference_of_new_primitive_types(self):
        """Demonstrates that a plugin can reference a primitive type sourced from another plugin and pass validation."""

        # Plugin A Definitions
        plugin_a_new_primitive_type = "new_primitive"
        plugin_a_primitive_extension = create_enum_ext_definition("primitive_extension", DEFINITION_NAME_PRIMITIVES, values=[plugin_a_new_primitive_type])

        self.plugin_a.register_definitions([plugin_a_primitive_extension])

        # Plugin B Definitions
        plugin_b_schema_field = create_field_entry("plugin_a_primitive", plugin_a_new_primitive_type)
        plugin_b_schema_fields = [plugin_b_schema_field]
        plugin_b_schema_definition = create_schema_definition("schemaB", fields=plugin_b_schema_fields)
        self.plugin_b.register_definitions([plugin_b_schema_definition])

        # Assert that plugin b fails validation when plugin a is not present.
        register_plugin(self.plugin_b)

        active_context = get_active_context(reload_context=True)
        context_sourced_plugin_a_definition = active_context.get_definition_by_name(plugin_a_primitive_extension.name)
        context_sourced_plugin_b_definition = active_context.get_definition_by_name(plugin_b_schema_definition.name)

        self.assertIsNone(context_sourced_plugin_a_definition)
        self.assertIsNotNone(context_sourced_plugin_b_definition)

        # Assert that the field in plugin b's definition sourced from plugin a is present.
        plugin_b_field_referencing_plugin_a, *_ = context_sourced_plugin_b_definition.get_fields()
        self.assertIsNotNone(plugin_b_field_referencing_plugin_a)
        self.assertEqual(plugin_a_new_primitive_type, plugin_b_field_referencing_plugin_a.get(DEFINITION_FIELD_TYPE))   ### TODO: POPO update ###

        # Perform validation on the definitions to demonstrate that plugin b is invalid.
        with self.assertRaises(ValidationError) as error:
            with validated_definitions([]):
                pass

            exception = error.exception
            self.assertEqual(ValidationError, type(exception))
            self.assertEqual(len(exception.args), 1)
            self.assertIn("undefined", exception.args[0].lower())

        # Assert that the plugin validation passes when both plugins are active.
        register_plugin(self.plugin_a)

        active_context = get_active_context(reload_context=True)
        context_sourced_plugin_a_definition = active_context.get_definition_by_name(plugin_a_primitive_extension.name)
        context_sourced_plugin_b_definition = active_context.get_definition_by_name(plugin_b_schema_definition.name)

        self.assertIsNotNone(context_sourced_plugin_a_definition)
        self.assertIsNotNone(context_sourced_plugin_b_definition)

        # Perform validation on the definitions to demonstrate that they're valid.
        actual_result = None
        with validated_definitions([]) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)
