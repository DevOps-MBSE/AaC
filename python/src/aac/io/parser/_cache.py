"""Provides a YAML Cache for parsed files or strings."""
import logging
from attr import Factory, attrib, attrs, validators
from hashlib import md5
from os.path import lexists
from typing import Optional
from yaml import Token

from aac.io.paths import sanitize_filesystem_path
from aac.io.parser._yaml import parse_yaml, scan_yaml

STRING_YAML_SOURCE = "string"


@attrs(hash=False)
class CacheEntry:
    """A cache entry for YAML strings.

    Attributes:
        hash (int): The hash value for the entry.
        yaml_structures (dict[str, Any]): A dictionary of string hashes to yaml dict/maps.
        yaml_tokens (list[Token]): A list of YAML tokens used to scan the content.
        times_accessed (int): The number of times this entry has been accessed.
    """
    hash: str = attrib(validator=validators.instance_of(str))
    yaml_structures: list[dict] = attrib(default=Factory(list), validator=validators.instance_of(list))
    yaml_tokens: list[Token] = attrib(default=Factory(list), validator=validators.instance_of(list))
    times_accessed: int = 0


@attrs
class YamlCache:
    """A YAML-Parsing cache for strings.

    Attributes:
        cache (dict[int, dict]): A dictionary of string hashes to yaml dict/maps.
    """

    cache: dict[str, CacheEntry] = attrib(default=Factory(dict), validator=validators.instance_of(dict))
    capacity: int = attrib(default=300, validator=validators.instance_of(int))

    def parse_string(self, string: str) -> list[dict]:
        """Parse the YAML string and return the YAML dictionaries."""
        return self._get_or_parse_string(STRING_YAML_SOURCE, string).yaml_structures

    def parse_file(self, file_path: str) -> list[dict]:
        """Parse the YAML file and return the YAML dictionaries."""
        yaml_maps = []
        sanitized_file_path = sanitize_filesystem_path(file_path)
        if lexists(sanitized_file_path):
            with open(sanitized_file_path) as yaml_file:
                file_content = yaml_file.read()
                yaml_maps = self._get_or_parse_string(sanitized_file_path, file_content).yaml_structures
        else:
            logging.error("Can't parse the file '{sanitized_file_path}' because it doesn't exist.")

        return yaml_maps

    def scan_string(self, string: str) -> list[Token]:
        """Parse the YAML string and return the YAML tokens."""
        return self._get_or_parse_string(STRING_YAML_SOURCE, string).yaml_tokens

    def scan_file(self, file_path: str) -> list[Token]:
        """Parse the YAML file and return the YAML tokens."""
        token_list = []
        sanitized_file_path = sanitize_filesystem_path(file_path)
        if lexists(sanitized_file_path):
            with open(sanitized_file_path) as yaml_file:
                file_content = yaml_file.read()
                token_list = self._get_or_parse_string(sanitized_file_path, file_content).yaml_tokens
        else:
            logging.error("Can't parse the file '{sanitized_file_path}' because it doesn't exist.")

        return token_list

    # Private Methods #

    def _get_entry(self, key: str) -> Optional[CacheEntry]:
        entry_to_return = self.cache.get(key)
        if entry_to_return:
            entry_to_return.times_accessed += 1

        return entry_to_return

    def _put_entry(self, key: str, value: CacheEntry) -> None:

        if len(self.cache) > self.capacity:
            cache_list: list[CacheEntry] = sorted(list(self.cache.values()), key=lambda x: x.times_accessed, reverse=True)
            entry_to_remove = cache_list[0]
            del self.cache[entry_to_remove.hash]

        self.cache[key] = value

    def _get_or_parse_string(self, content_source: str, content_string: str) -> CacheEntry:
        """Get the cached entry or parse the string and cache it."""
        content_hash = str(md5(content_string.encode()))
        cached_dict = self._get_entry(content_hash)

        if not cached_dict:
            yaml_dicts = parse_yaml(content_source, content_string)
            yaml_tokens = scan_yaml(content_string)
            cached_dict = CacheEntry(content_hash, yaml_dicts, yaml_tokens)
            self._put_entry(cached_dict.hash, cached_dict)
        else:
            logging.info("hi")

        return cached_dict


# Singleton for shared cache access
YAML_CACHE: YamlCache = YamlCache()
