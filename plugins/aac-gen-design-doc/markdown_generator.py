from document_generator import DesignDocumentGenerator


class InvalidLevelError(RuntimeError):
    pass


class MarkdownDesignDocumentGenerator(DesignDocumentGenerator):
    MIN_LEVEL: int = 1
    MAX_LEVEL: int = 6

    def make_document_outline(self, model: dict) -> str:
        """Returns a markdown document outline based on `model`.

        Args:
            `model` <dict>: The model based on which to generate the document outline.

        Returns:
            A markdown document outline for the provided `model`.
        """
        level = 1

        def maybe_make_section(name, model):
            aac_type = list(model.keys())[0]
            if aac_type not in ["usecase", "model"]:
                return ""

            title = f"{aac_type.capitalize()}: {name}"
            content = model[aac_type]["description"]
            return self.make_section(title, level, content) + "\n"

        return "\n".join(list(map(maybe_make_section, model.keys(), model.values())))

    def make_section(self, title: str, level: int, text: str) -> str:
        """Returns a markdown section with a heading and `text` content.

        Args:
            `title` <str>: The title to be used for the section.
            `level` <int>: The heading level for the section.
            `text` <str>: The text to use as the content of the section.

        Returns:
            A string representing a markdown section with a heading and the specified `text`.

        Raises:
            <InvalidLevelError>: If the provided `level` is less than `MIN_LEVEL` or greater than
            `MAX_LEVEL`, an <InvalidLevelError> is raised.

        See also:
            `make_heading`
            `MIN_LEVEL`
            `MAX_LEVEL`
        """
        return f"{self.make_heading(title, level)}\n\n{text}"

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

    def make_link(self, text: str, url: str, label: str = None) -> str:
        """Returns"""

        def make_reference_link():
            return f"[{text}][{label}]\n\n[{label}]: {url}"

        def make_standard_link():
            return f"[{text}]({url})"

        return make_reference_link() if label else make_standard_link()

    def make_ordered_list(self, items: list[str]) -> str:
        """Returns an ordered markdown list.

        Args:
            `items` <list[str]>: The list of items to be placed in the ordered list.

        Returns:
            A string representing an ordered list of `items` in markdown format.
        """
        return self._make_list("1.", items)

    def make_unordered_list(self, items: list[str]) -> str:
        """Returns an unordered markdown list.

        Args:
            `items` <list[str]>: The list of items to be placed in the unordered list.

        Returns:
            A string representing an unordered list of `items` in markdown format.
        """
        return self._make_list("-", items)

    def _make_list(self, prefix: str, items: list[str]) -> str:
        return "\n".join(list(map(lambda i: f"{prefix} {i}", items)))

    def make_code_line(self, code: str) -> str:
        """Returns an inline `code` string in markdown.

        Args:
            `code` <str>: The string to be returned as a line of code in markdown.

        Returns:
            A string representing inline `code` in markdown.
        """
        return self._surround(code, "`")

    def make_code_block(self, code: str, language: str = "") -> str:
        """Returns an block of code in markdown.

        Args:
            `code` <str>: The string to be returned as a block of code in markdown.
            `language` <str>: The name of the language the `code` is written in.

        Returns:
            A string representing a block of `code` in markdown.
        """
        return f"```{language}\n{code}\n```"
