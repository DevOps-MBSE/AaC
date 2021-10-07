import unittest
import ArchUtil


class TestArchUtil(unittest.TestCase):

    def test_get_primitive(self):
        expected_results = ["int", "number", "string", "bool", "file", "date"]

        result = ArchUtil.getPrimitives()

        self.assertCountEqual(result, expected_results)

    def test_getAaCSpec(self):

        aac_data, aac_enums = ArchUtil.getAaCSpec()

        self.assertTrue(len(aac_data.keys()) > 0)
        self.assertTrue(len(aac_data.keys()) > 0)

    def test_search(self):

        data_entry = {'data': {'fields': [
            {'name': 'name', 'type': 'string'},
            {'name': 'type', 'type': 'BehaviorType'},
            {'name': 'description', 'type': 'string'},
            {'name': 'tags', 'type': 'string[]'},
            {'name': 'input', 'type': 'Field[]'},
            {'name': 'output', 'type': 'Field[]'},
            {'name': 'acceptance', 'type': 'Scenario[]'}],
            'name': 'Behavior',
            'required': ['name', 'type', 'acceptance']}}

        expected = ["string", "BehaviorType", "string", "string[]", "Field[]", "Field[]", "Scenario[]"]
        data_model_types = ArchUtil.search(data_entry, ["data", "fields", "type"])

        print(data_model_types)

        self.assertCountEqual(data_model_types, expected)
