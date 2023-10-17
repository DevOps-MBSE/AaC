"""Provides a YAML Cache for parsed files or strings."""
import logging
from attr import Factory, attrib, attrs, validators
from hashlib import md5
from os.path import lexists
from typing import Optional
from yaml import Token

from aac.in_out.paths import sanitize_filesystem_path
from aac.in_out.parser._yaml import parse_yaml, scan_yaml

STRING_YAML_SOURCE = "string"


@attrs(hash=False)
class CacheEntry:
    """A cache entry for YAML strings.

    Attributes:
        hash (str): The hash value for the entry.
        yaml_structures (dict[str, Any]): A dictionary of string hashes to yaml dict/maps.
        yaml_tokens (list[Token]): A list of YAML tokens used to scan the content.
        times_accessed (int): The number of times this entry has been accessed.
    """
    hash: str = attrib(validator=validators.instance_of(str))
    yaml_structures: list[dict] = attrib(default=Factory(list), validator=validators.instance_of(list))
    yaml_tokens: list[Token] = attrib(default=Factory(list), validator=validators.instance_of(list))
    times_accessed: int = 0


@attrs
class YamlLFUCache:
    """A Least Frequently Used (LFU) YAML-Parsing cache for strings.

    Attributes:
        capacity (int): The number of cached files/strings before clearing space according to LFU cache behavior.
        cache (dict[str, CacheEntry]): The internal cache data structure -- this is intended to be private, don't access it directly.
    """

    capacity: int = attrib(default=300, validator=validators.instance_of(int))
    # The internal cache is using a dict with sorting O(n log n) rather than a more complex linked list which would be capable of linear time
    cache: dict[str, CacheEntry] = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def parse_string(self, string: str, source: str = STRING_YAML_SOURCE) -> list[dict]:
        """Parse the YAML string and return the YAML dictionaries."""
        yaml_dicts = self._get_or_parse_string(source, string).yaml_structures
        return yaml_dicts

    def parse_file(self, file_path: str) -> list[dict]:
        """Parse the YAML file and return the YAML dictionaries."""
        yaml_dicts = []
        file_cache_entry = self._get_file_content_cache_entry(file_path)

        if file_cache_entry:
            yaml_dicts = file_cache_entry.yaml_structures

        return yaml_dicts

    def scan_string(self, string: str, source: str = STRING_YAML_SOURCE) -> list[Token]:
        """Parse the YAML string and return the YAML tokens."""
        return self._get_or_parse_string(source, string).yaml_tokens

    def scan_file(self, file_path: str) -> list[Token]:
        """Parse the YAML file and return the YAML tokens."""
        token_list = []
        file_cache_entry = self._get_file_content_cache_entry(file_path)

        if file_cache_entry:
            token_list = file_cache_entry.yaml_tokens

        return token_list

    # Private Methods #

    def _get_file_content_cache_entry(self, file_path: str) -> Optional[CacheEntry]:
        sanitized_file_path = sanitize_filesystem_path(file_path)
        cache_entry = None
        if lexists(sanitized_file_path):
            with open(sanitized_file_path) as yaml_file:
                file_content = yaml_file.read()
                cache_entry = self._get_or_parse_string(sanitized_file_path, file_content)
        else:
            logging.error(f"Can't parse the file '{sanitized_file_path}' because it doesn't exist.")

        return cache_entry

    def _get_entries_sorted_by_access_count(self) -> list[CacheEntry]:
        return sorted(list(self.cache.values()), key=lambda x: x.times_accessed, reverse=True)

    def _get_entry(self, key: str) -> Optional[CacheEntry]:
        entry_to_return = self.cache.get(key)
        if entry_to_return:
            entry_to_return.times_accessed += 1

        return entry_to_return

    def _put_entry(self, key: str, value: CacheEntry) -> None:

        if len(self.cache) >= self.capacity:
            entry_to_pop, *_ = self._get_entries_sorted_by_access_count()
            self.cache.pop(entry_to_pop.hash)
            logging.debug(f"The YAML parser cache has hit its limits, clearing space for a new entry. Current capacity: {self.capacity}")

        self.cache[key] = value

    def _get_or_parse_string(self, content_source: str, content_string: str) -> CacheEntry:
        """Get the cached entry or parse the string and cache it."""
        content_hash = str(md5(content_string.encode()).hexdigest())
        cache_entry = self._get_entry(content_hash)

        if not cache_entry:
            yaml_dicts = parse_yaml(content_source, content_string)
            yaml_tokens = scan_yaml(content_source, content_string)
            cache_entry = CacheEntry(content_hash, yaml_dicts, yaml_tokens)
            self._put_entry(cache_entry.hash, cache_entry)

        return cache_entry
