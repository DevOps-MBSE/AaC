"""This module manages a singleton instance of the YAML Parser Cache."""
from aac.io.parser._cache import YamlCache


YAML_CACHE: YamlCache = None


def get_cache() -> YamlCache:
    """
    Return the YAML Parser Cache instance.

    Returns:
        The YAML Parser Cache instance
    """
    global YAML_CACHE

    if not YAML_CACHE:
        YAML_CACHE = YamlCache()

    return YAML_CACHE


def reset_cache() -> None:
    """Resets the cache clearing all data."""
    global YAML_CACHE
    YAML_CACHE = YamlCache()
