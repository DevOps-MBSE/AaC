from unittest import TestCase
from jinja2 import Template

from aac import template_engine


class TestTemplateEngine(TestCase):
    def test_load_templates(self):
        templates = template_engine.load_templates("genplug")
        self.assertGreater(len(templates), 0)

    def test_generate_template(self):
        expected_string = "my first name is John and my last name is Doe"
        template = Template("my first name is {{name.first}} and my last name is {{name.last}}")
        properties = {"name": {"first": "John", "last": "Doe"}}

        actual_string = template_engine.generate_template(template, properties)

        self.assertEqual(expected_string, actual_string)

    def test_generate_templates(self):
        expected_strings = [
            "my first name is John and my last name is Doe",
            "my last name is Doe and my first name is John",
        ]

        templates = [
            Template("my first name is {{name.first}} and my last name is {{name.last}}"),
            Template("my last name is {{name.last}} and my first name is {{name.first}}"),
        ]

        for i in range(len(templates)):
            templates[i].name = f"template{i}"

        properties = {"name": {"first": "John", "last": "Doe"}}

        actual_strings = template_engine.generate_templates(templates, properties)

        self.assertEqual(expected_strings[0], actual_strings.get(templates[0].name))
        self.assertEqual(expected_strings[1], actual_strings.get(templates[1].name))
