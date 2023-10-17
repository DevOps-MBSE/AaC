"""This module manages a singleton instance of the YAML Parser Cache."""
from aac.in_out.parser._cache import YamlLFUCache


YAML_CACHE: YamlLFUCache = None


def get_cache() -> YamlLFUCache:
    """
    Return the YAML Parser Cache instance.

    Returns:
        The YAML Parser Cache instance
    """
    global YAML_CACHE

    if not YAML_CACHE:
        YAML_CACHE = YamlLFUCache()

    return YAML_CACHE


def reset_cache() -> None:
    """Resets the cache clearing all data."""
    global YAML_CACHE
    YAML_CACHE = YamlLFUCache()
