from os import listdir
from os.path import basename, lexists
from tempfile import TemporaryDirectory
from unittest.mock import patch

from aac.io.files.aac_file import AaCFile
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_NAME_PRIMITIVES
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.active_context.active_context_impl import (
    list_files,
    list_definitions,
    describe_definition,
    import_state,
    export_state,
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.io import new_working_dir, TemporaryTestFile
from tests.helpers.parsed_definitions import create_field_entry, create_schema_definition


class TestActiveContextPlugin(ActiveContextTestCase):
    definition = create_schema_definition("TestDefinition", fields=[create_field_entry("a", "int")])

    def test_list_files(self):
        result = list_files()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

        test_context = get_active_context()
        expected_files = [file.uri for file in test_context.get_files_in_context()]
        actual_files = result.get_messages_as_string()
        self.assertGreater(len(actual_files), 0)

        for expected_file in expected_files:
            self.assertIn(expected_file, actual_files)

    def test_list_definitions(self):
        result = list_definitions()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

        for name in get_active_context().get_defined_types():
            self.assertIn(name, result.get_messages_as_string())

    def test_describe_definition_not_in_context(self):
        definition_name = "IAmNotInContext"
        result = describe_definition(definition_name=definition_name)
        self.assertRegexpMatches(result.get_messages_as_string(), f"{definition_name}.*not.*in.*context")

    def test_describe_definition_in_context(self):
        definition_name = DEFINITION_NAME_PRIMITIVES

        result = describe_definition(definition_name=definition_name)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        primitives_definition = get_active_context().get_definition_by_name(definition_name)
        self.assertIn(primitives_definition.source.uri, result.get_messages_as_string())
        self.assertIn(f"{primitives_definition.lexemes[0].location.line + 1}", result.get_messages_as_string())
        self.assertIn(primitives_definition.to_yaml(), result.get_messages_as_string())

    def test_import_state_success(self):
        from aac.plugins.first_party.gen_design_doc import plugin_name

        with (
            TemporaryTestFile("", mode="w+") as state_file,
            patch("aac.lang.active_context_lifecycle_manager.ACTIVE_CONTEXT_STATE_FILE_NAME", state_file.name),
        ):
            test_context = get_active_context(reload_context=True)
            test_context.deactivate_plugin_by_name(plugin_name)
            test_context.export_to_file(state_file.name)
            test_context = get_active_context(reload_context=True)

            result = import_state(state_file=state_file.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            success_message_regex = f"success.*import.*{basename(state_file.name)}"
            self.assertRegexpMatches(result.get_messages_as_string().lower(), success_message_regex)

            self.assertIn(DEFINITION_NAME_PRIMITIVES, test_context.get_defined_types())

            active_plugin_names = [plugin.name for plugin in test_context.get_active_plugins()]
            self.assertNotIn(plugin_name, active_plugin_names)

            inactive_plugin_names = [plugin.name for plugin in test_context.get_inactive_plugins()]
            self.assertIn(plugin_name, inactive_plugin_names)

    def test_import_state_failure(self):
        nonexisting_file = "/fake/file/path"
        result = import_state(state_file=nonexisting_file)
        self.assertNotEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

        failure_message_regex = f"{basename(nonexisting_file)}.*not.*exist"
        self.assertRegexpMatches(result.get_messages_as_string().lower(), failure_message_regex)

    def test_export_state_no_overwrite(self):
        with TemporaryDirectory() as tmpdir, new_working_dir(tmpdir):
            self.assertEqual(len(listdir(tmpdir)), 0)

            state_file_name = "tmp-state.json"
            result = export_state(state_file_name=state_file_name, overwrite=False)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            success_message_regex = f"success.*export.*{state_file_name}"
            self.assertRegexpMatches(result.get_messages_as_string().lower(), success_message_regex)

            self.assertListEqual(listdir(tmpdir), [state_file_name])

            result = export_state(state_file_name=state_file_name, overwrite=False)
            self.assertNotEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            failure_message_regex = f"{state_file_name}.*exists.*overwrite"
            self.assertRegexpMatches(result.get_messages_as_string().lower(), failure_message_regex)

    def test_export_state_overwrite(self):
        replaceable_content = "replacable content"
        with TemporaryTestFile(replaceable_content, mode="w+") as state_file:
            self.assertTrue(lexists(state_file.name))
            self.assertEqual(state_file.read(), replaceable_content)

            result = export_state(state_file_name=state_file.name, overwrite=True)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            success_message_regex = f"success.*export.*{basename(state_file.name)}"
            self.assertRegexpMatches(result.get_messages_as_string().lower(), success_message_regex)

            self.assertNotEqual(state_file.read(), replaceable_content)

    def file_names_to_string(self, files: list[AaCFile]) -> str:
        return "\n".join([file.uri for file in files])
