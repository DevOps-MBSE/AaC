from unittest import TestCase
from aac.in_out.parser import get_cache
from aac.in_out.parser._cache import YamlLFUCache
from aac.context.language_context import LanguageContext

MODEL_TEMPLATE = """
model:
  name: __name__
  description: This is a test model with no content.
"""


class TestParserCache(TestCase):
    def test_get_cache_has_core_spec(self):
        parser_cache = get_cache()

        context = LanguageContext()
        expected_spec_definitions = [definition.structure for definition in context.get_aac_core_definitions()]
        actual_spec_definitions_from_file = parser_cache.parse_file(context.get_aac_core_file_path())
        actual_spec_definitions_from_string = parser_cache.parse_string(context.get_aac_core_as_yaml())

        # Assert parse via filename is equivalent to expected core spec
        self.assertListEqual(expected_spec_definitions, actual_spec_definitions_from_file)

        # Assert parse via file content is equivalent to expected core spec
        self.assertListEqual(expected_spec_definitions, actual_spec_definitions_from_string)

    def test_cache_parse_ejects_least_frequently_used_content(self):
        parser_capacity = 4
        parser_cache = YamlLFUCache(capacity=parser_capacity)

        used_definition_1_name = "used_definition_1"
        used_definition_1 = MODEL_TEMPLATE.replace("__name__", used_definition_1_name)

        used_definition_2_name = "used_definition_2"
        used_definition_2 = MODEL_TEMPLATE.replace("__name__", used_definition_2_name)

        used_definition_3_name = "used_definition_3"
        used_definition_3 = MODEL_TEMPLATE.replace("__name__", used_definition_3_name)

        used_definition_4_name = "used_definition_4"
        used_definition_4 = MODEL_TEMPLATE.replace("__name__", used_definition_4_name)

        unused_definition_1_name = "unused_definition_1"
        unused_definition_1 = MODEL_TEMPLATE.replace("__name__", unused_definition_1_name)

        # Assert the cache is empty at the beginning
        self.assertEqual(0, len(parser_cache.cache))

        # Parse and cache the test strings
        parsed_unused_definition_1 = parser_cache.parse_string(unused_definition_1)[0]
        parser_cache.parse_string(used_definition_1)
        parser_cache.parse_string(used_definition_2)
        parser_cache.parse_string(used_definition_3)

        # Assert the cache is full at the end
        self.assertEqual(parser_capacity, len(parser_cache.cache))

        # Re-parse the used definitions to bump their use count per parse
        parser_cache.parse_string(used_definition_1)
        parser_cache.parse_string(used_definition_1)
        parser_cache.parse_string(used_definition_1)

        parser_cache.parse_string(used_definition_2)
        parser_cache.parse_string(used_definition_2)

        parser_cache.parse_string(used_definition_3)

        # Grab and sort the parser cache entries since their stored internally in an unordered hash map.
        cached_values = parser_cache._get_entries_sorted_by_access_count()
        # Assert the order of the cached entries
        self.assertEqual(3, cached_values[0].times_accessed)
        self.assertEqual(2, cached_values[1].times_accessed)
        self.assertEqual(1, cached_values[2].times_accessed)
        self.assertEqual(0, cached_values[3].times_accessed)

        # Assert that the last element in the cache is the unused definition
        expected_unused_entry = parser_cache._get_entries_sorted_by_access_count().pop(-1)
        expected_unused_dict, *_ = expected_unused_entry.yaml_structures
        self.assertDictEqual(expected_unused_dict, parsed_unused_definition_1)

        # Parse the new used string
        parsed_used_definition_4 = parser_cache.parse_string(used_definition_4)[0]

        # Assert that the last element in the cache is the last used definition
        expected_used_entry = parser_cache._get_entries_sorted_by_access_count().pop(-1)
        expected_used_dict, *_ = expected_used_entry.yaml_structures
        self.assertDictEqual(expected_used_dict, parsed_used_definition_4)

        # Assert the cache is full at the end
        self.assertEqual(parser_capacity, len(parser_cache.cache))
