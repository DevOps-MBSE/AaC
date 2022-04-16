from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.material_model.material_model_impl import gen_bom


class TestMaterial_model(TestCase):
    def test_gen_bom(self):
        # TODO: Write tests for gen_bom

        architecture_file = str()
        output_directory = str()
        
        result = gen_bom(architecture_file=architecture_file, output_directory=output_directory)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
