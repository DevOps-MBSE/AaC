"""Helpers for serializing an AaC Language Context to JSON."""

from json import JSONEncoder

from aac import __version__
from aac.lang.language_context import LanguageContext


class LanguageContextEncoder(JSONEncoder):
    """Allow a LanguageContext to be JSON-encoded."""

    def default(self, object: LanguageContext):
        """Return a JSON-serializable version of a language context."""
        if isinstance(object, LanguageContext):
            return {
                "aac_version": __version__,
                "files": [file.uri for file in object.get_files_in_context()],
                "definitions": [definition.name for definition in object.definitions],
                "plugins": [plugin.name for plugin in object.plugins],
            }

        return JSONEncoder.default(self, object)
