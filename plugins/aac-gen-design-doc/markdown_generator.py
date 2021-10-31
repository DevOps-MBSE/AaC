from document_generator import DesignDocumentGenerator


class InvalidLevelError(RuntimeError):
    pass


class MarkdownDesignDocumentGenerator(DesignDocumentGenerator):
    MIN_LEVEL: int = 1
    MAX_LEVEL: int = 6

    def make_heading(self, title: str, level: int) -> str:
        """Returns a markdown heading with the specified `title`, at the specified `level`.

        Args:
            `title` <str>: The title to be used for the heading.
            `level` <int>: The heading level.

        Returns:
            A string representing a heading at the specified `level`, with the specified `title`.

        Raises:
            <InvalidLevelError>: If the provided `level` is less than `MIN_LEVEL` or greater than
            `MAX_LEVEL`, an <InvalidLevelError> is raised.

        See also:
            `MIN_LEVEL`
            `MAX_LEVEL`
        """
        min_level = self.MIN_LEVEL
        max_level = self.MAX_LEVEL

        if min_level <= level <= max_level:
            return f"{'#' * level} {title}"

        error = f"invalid level: {level}; valid levels {min_level} to {max_level}"
        raise InvalidLevelError(error)
