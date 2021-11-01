import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from jinja2 import Template

from aac.template_engine import (TemplateOutputFile, generate_template,
                                 generate_templates, load_default_templates,
                                 write_generated_templates_to_file)


class TestTemplateEngine(TestCase):
    def test_load_templates(self):
        templates = load_default_templates("genplug")
        self.assertGreater(len(templates), 0)

    def test_generate_template(self):
        expected_string = "my first name is John and my last name is Doe"
        template = Template("my first name is {{name.first}} and my last name is {{name.last}}")
        properties = {"name": {"first": "John", "last": "Doe"}}

        actual_string = generate_template(template, properties)

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

        actual_strings = generate_templates(templates, properties)

        self.assertEqual(expected_strings[0], actual_strings.get(templates[0].name))
        self.assertEqual(expected_strings[1], actual_strings.get(templates[1].name))

    def test_write_generated_templates_to_file(self):
        template_name = "myTemplate.test"
        template_content = "This is the sample content in my template"
        templates = [TemplateOutputFile(template_name, template_content, True)]

        with TemporaryDirectory() as temp_directory:
            write_generated_templates_to_file(templates, temp_directory)
            temp_directory_files = os.listdir(temp_directory)

            for template in templates:
                self.assertEqual(len(templates), len(temp_directory_files))
                self.assertIn(template.file_name, temp_directory_files)

                with open(os.path.join(temp_directory, template.file_name)) as file:
                    self.assertEqual(template.content, file.read())
