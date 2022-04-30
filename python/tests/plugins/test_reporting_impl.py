from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.reporting.reporting_impl import report, report_csv


class TestReporting(TestCase):
    def test_report(self):
        # TODO: Write tests for report

        architecture_file = str()
        output_file = str()
        
        result = report(architecture_file=architecture_file, output_file=output_file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
    def test_report_csv(self):
        # TODO: Write tests for report_csv

        architecture_file = str()
        output_file = str()
        
        result = report_csv(architecture_file=architecture_file, output_file=output_file)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
    
