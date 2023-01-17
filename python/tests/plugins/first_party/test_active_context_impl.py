from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.active_context.active_context_impl import list_files, remove_file, add_file, reset_context, list_definitions, describe_definition, import_state, export_state


class TestActiveContext(TestCase):
    def test_list_files(self):
        # TODO: Write tests for list_files

        
        result = list_files()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
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
    
    def test_describe_definition(self):
        # TODO: Write tests for describe_definition

        definition-name = str()
        
        result = describe_definition(definition-name=definition-name)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
    def test_import_state(self):
        # TODO: Write tests for import_state

        state-file = str()
        
        result = import_state(state-file=state-file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
    def test_export_state(self):
        # TODO: Write tests for export_state

        state-file-name = str()
        overwrite = bool()
        
        result = export_state(state-file-name=state-file-name, overwrite=overwrite)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
