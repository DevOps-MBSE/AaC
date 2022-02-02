import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from jinja2 import Template

from aac.template_engine import (
    TemplateOutputFile,
    generate_template_as_string,
    generate_template,
    generate_templates_as_strings,
    load_default_templates,
    write_generated_templates_to_file,
)


class TestTemplateEngine(TestCase):
    def test_load_templates(self):
        templates = load_default_templates("genplug")
        self.assertGreater(len(templates), 0)

    def test_generate_template(self):
        expected_output = TemplateOutputFile("template.py", "my first name is John and my last name is Doe", False)

        template = Template("my first name is {{name.first}} and my last name is {{name.last}}")
        template.name = "template.py"  # This would have been set by the template loader
        properties = {"name": {"first": "John", "last": "Doe"}}

        actual_output = generate_template(template, properties)

        self.assertEqual(expected_output, actual_output)

    def test_generate_template_as_string(self):
        expected_string = "my first name is John and my last name is Doe"
        template = Template("my first name is {{name.first}} and my last name is {{name.last}}")
        properties = {"name": {"first": "John", "last": "Doe"}}

        actual_string = generate_template_as_string(template, properties)

        self.assertEqual(expected_string, actual_string)

    def test_generate_templates_as_strings(self):
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

        actual_strings = generate_templates_as_strings(templates, properties)

        self.assertEqual(expected_strings[0], actual_strings.get(templates[0].name))
        self.assertEqual(expected_strings[1], actual_strings.get(templates[1].name))

    def test_write_generated_templates_to_file(self):
        test_template_one = TemplateOutputFile("myTemplate.test", "This is the sample content in my template", True)
        test_template_one.file_name = "temp1"

        test_template_two = TemplateOutputFile("myOtherTemplate.test", "This is the other sample content in my template", True)
        test_template_two.file_name = "temp2"

        templates = [test_template_one, test_template_two]

        with TemporaryDirectory() as temp_directory:
            write_generated_templates_to_file(templates, temp_directory)
            temp_directory_files = os.listdir(temp_directory)

            self.assertEqual(len(templates), len(temp_directory_files))

            for i in range(len(templates)):
                expected_template = templates[i]

                self.assertIn(expected_template.file_name, temp_directory_files)

                with open(os.path.join(temp_directory, expected_template.file_name)) as file:
                    self.assertEqual(expected_template.content, file.read())

    def test_write_generated_templates_to_file_in_directory(self):
        test_template = TemplateOutputFile(
            "template.test", "The sample content.", False, parent_dir="tests"
        )
        test_template.file_name = "temp"

        self.assertIsNotNone(test_template)
        self.assertEqual(test_template.file_name, "temp")
        self.assertEqual(test_template.parent_dir, "tests")

        with TemporaryDirectory() as temp_dir:
            write_generated_templates_to_file([test_template], temp_dir)
            temp_dir_files = os.listdir(temp_dir)

            self.assertEqual(len(temp_dir_files), 1)
            self.assertIn(test_template.parent_dir, temp_dir_files)

            test_file = os.path.join(temp_dir, test_template.parent_dir, test_template.file_name)
            with open(test_file) as file:
                self.assertEqual(test_template.content, file.read())
