from unittest import TestCase

from aac.lang.definitions.definition import Definition
from aac.io.parser import get_cache
from aac.io.parser._cache import YamlCache
from aac.spec.core import get_aac_spec, get_aac_spec_as_yaml, _get_aac_spec_file_path
from tests.active_context_test_case import ActiveContextTestCase

from tests.helpers.parsed_definitions import create_model_definition


class TestParserCache(ActiveContextTestCase):
    def test_get_cache_has_core_spec(self):
        parser_cache = get_cache()

        expected_spec_definitions = [definition.structure for definition in get_aac_spec()]
        actual_spec_definitions_from_file = parser_cache.parse_file(_get_aac_spec_file_path())
        actual_spec_definitions_from_string = parser_cache.parse_string(get_aac_spec_as_yaml())

        # Assert parse via filename is equivalent to expected core spec
        self.assertListEqual(expected_spec_definitions, actual_spec_definitions_from_file)

        # Assert parse via file content is equivalent to expected core spec
        self.assertListEqual(expected_spec_definitions, actual_spec_definitions_from_string)

    def test_cache_parse_ejects_least_frequently_used_content(self):
        parser_capacity = 4
        parser_cache = YamlCache(capacity=parser_capacity)

        used_definition_1_name = "used_definition_1"
        used_definition_1 = create_model_definition(used_definition_1_name)

        used_definition_2_name = "used_definition_2"
        used_definition_2 = create_model_definition(used_definition_2_name)

        used_definition_3_name = "used_definition_3"
        used_definition_3 = create_model_definition(used_definition_3_name)

        used_definition_4_name = "used_definition_4"
        used_definition_4 = create_model_definition(used_definition_4_name)

        unused_definition_1_name = "unused_definition_1"
        unused_definition_1 = create_model_definition(unused_definition_1_name)

        # Assert the cache is empty at the beginning
        self.assertEqual(0, len(parser_cache.cache))

        # Parse and cache the test strings
        parser_cache.parse_string(unused_definition_1.content)
        parser_cache.parse_string(used_definition_1.content)
        parser_cache.parse_string(used_definition_2.content)
        parser_cache.parse_string(used_definition_3.content)

        # Assert the cache is full at the end
        self.assertEqual(parser_capacity, len(parser_cache.cache))

        # Re-parse the used definitions to bump their use count per parse
        parser_cache.parse_string(used_definition_1.content)
        parser_cache.parse_string(used_definition_1.content)
        parser_cache.parse_string(used_definition_1.content)

        parser_cache.parse_string(used_definition_2.content)
        parser_cache.parse_string(used_definition_2.content)

        parser_cache.parse_string(used_definition_3.content)

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
        self.assertDictEqual(expected_unused_dict, unused_definition_1.structure)

        # Parse the new used string
        parser_cache.parse_string(used_definition_4.content)

        # Assert that the last element in the cache is the last used definition
        expected_used_entry = parser_cache._get_entries_sorted_by_access_count().pop(-1)
        expected_used_dict, *_ = expected_used_entry.yaml_structures
        self.assertDictEqual(expected_used_dict, used_definition_4.structure)

        # Assert the cache is full at the end
        self.assertEqual(parser_capacity, len(parser_cache.cache))
