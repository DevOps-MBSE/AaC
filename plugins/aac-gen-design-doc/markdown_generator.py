from document_generator import DesignDocumentGenerator


class InvalidLevelError(RuntimeError):
    pass


class MarkdownDesignDocumentGenerator(DesignDocumentGenerator):
    MIN_LEVEL: int = 1
    MAX_LEVEL: int = 6

    def make_heading(self, title: str, level: int):
        """Returns a markdown heading for the specified ITEM.

        Args:
            title <str>: The title to be used for the heading.
            level <int>: The level to make the heading - must be an integer between 1 and 6, inclusive.

        Returns:
            A string representing a markdown heading at the specified level, with the specified title.
        """
        min_level = self.MIN_LEVEL
        max_level = self.MAX_LEVEL

        if min_level <= level <= max_level:
            return f"{'#' * level} {title}"

        error = f"invalid level: {level}; valid levels {min_level} to {max_level}"
        raise InvalidLevelError(error)
