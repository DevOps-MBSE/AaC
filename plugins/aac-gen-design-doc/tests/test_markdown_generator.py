from unittest import TestCase

from markdown_generator import (InvalidLevelError,
                                MarkdownDesignDocumentGenerator)


class MarkdownDesignDocumentGeneratorTest(TestCase):
    markdown = None
    title = "test title"

    def setUp(self):
        self.markdown = MarkdownDesignDocumentGenerator()

    def test_can_make_headings_one_through_six(self):
        def assertion(i):
            title = self.title
            make_heading = self.markdown.make_heading
            self.assertEqual(make_heading(title, i), f"{'#' * i} {title}")

        list(map(assertion, range(1, 7)))

    def test_make_heading_fails_when_given_level_out_of_bounds(self):
        title = self.title
        make_heading = self.markdown.make_heading

        self.assertRaisesRegex(InvalidLevelError, "invalid.*0.*1", make_heading, title, 0)
        self.assertRaisesRegex(InvalidLevelError, "invalid.*7.*6", make_heading, title, 7)

    def test_can_make_section_with_headings(self):
        def assertion(i):
            title = self.title
            content = "some test content"
            make_section = self.markdown.make_section
            self.assertEqual(
                make_section(title, i, content),
                f"{self.markdown.make_heading(title, i)}\n\n{content}",
            )

        list(map(assertion, range(1, 7)))

    def test_make_section_fails_when_given_level_out_of_bounds(self):
        title = self.title
        make_section = self.markdown.make_section

        self.assertRaisesRegex(InvalidLevelError, "invalid.*0.*1", make_section, title, 0, "text")
        self.assertRaisesRegex(InvalidLevelError, "invalid.*7.*6", make_section, title, 7, "text")
