from aac.io.files.aac_file import AaCFile
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_NAME_PRIMITIVES
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.active_context.active_context_impl import (
    list_files,
    remove_file,
    add_file,
    reset_context,
    list_definitions,
    describe_definition,
    import_state,
    export_state,
)

from tests.active_context_test_case import ActiveContextTestCase


class TestActiveContext(ActiveContextTestCase):
    def test_list_files(self):
        result = list_files()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

        test_context = get_active_context()
        self.assertEqual(result.get_messages_as_string(), self.file_names_to_string(test_context.get_files_in_context()))

    def test_remove_file(self):
        # TODO: Write tests for remove_file

        file = str()

        result = remove_file(file=file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_add_file(self):
        # TODO: Write tests for add_file

        file = str()

        result = add_file(file=file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_reset_context(self):
        # TODO: Write tests for reset_context

        result = reset_context()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_list_definitions(self):
        # TODO: Write tests for list_definitions

        result = list_definitions()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_describe_definition_not_in_context(self):
        definition_name = "IAmNotInContext"
        result = describe_definition(definition_name=definition_name)
        self.assertRegexpMatches(result.get_messages_as_string(), f"{definition_name}.*not.*in.*context")

    def test_describe_definition_in_context(self):
        definition_name = DEFINITION_NAME_PRIMITIVES

        result = describe_definition(definition_name=definition_name)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        self.assertIn("spec.yaml", result.get_messages_as_string())
        self.assertIn("255", result.get_messages_as_string())

    def test_import_state(self):
        # TODO: Write tests for import_state

        state_file = str()

        result = import_state(state_file=state_file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_export_state(self):
        # TODO: Write tests for export_state

        state_file_name = str()
        overwrite = bool()

        result = export_state(state_file_name=state_file_name, overwrite=overwrite)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def file_names_to_string(self, files: list[AaCFile]) -> str:
        return "\n".join([file.uri for file in files])
