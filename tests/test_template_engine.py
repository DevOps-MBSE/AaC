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

    def test_generate_template(self):
        templates = template_engine.load_templates("genplug")
        properties = {
            "plugin": {"name": "test"},
            "commands": [
                {
                    "name": "test-command",
                    "description": "Some long test command description for my test function.",
                    "input": [{"name": "input1", "type": "str"}],
                }
            ],
        }
        templatesStr = template_engine.generate_templates(templates, properties)
        for stri in templatesStr:
            print(f"----- {stri} -----")
            print(templatesStr.get(stri))
            print()
