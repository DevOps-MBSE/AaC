import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from jinja2 import Template

from aac.template_engine import (
    TemplateOutputFile,
    generate_template_as_string,
    generate_template,
    generate_templates_as_strings,
    load_templates,
    write_generated_templates_to_file,
)
from aac.plugins.gen_plugin import __package__ as gen_plugin_package

from tests.helpers.io import temporary_test_file


class TestTemplateEngine(TestCase):
    def test_load_templates(self):
        templates = load_templates(gen_plugin_package)
        self.assertGreater(len(templates), 0)

    def test_generate_template(self):
        with TemporaryDirectory() as temp_dir:
            expected_output = TemplateOutputFile(
                output_directory=temp_dir,
                template_name="template.py",
                content="my first name is John and my last name is Doe",
                overwrite=False
            )

            template = Template("my first name is {{name.first}} and my last name is {{name.last}}")
            template.name = "template.py"  # This would have been set by the template loader
            properties = {"name": {"first": "John", "last": "Doe"}}

            actual_output = generate_template(template, temp_dir, properties)

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
        with TemporaryDirectory() as temp_directory:
            test_template_one = TemplateOutputFile(
                output_directory=temp_directory,
                template_name="myTemplate.test",
                content="This is the sample content in my template",
                overwrite=True
            )
            test_template_one.file_name = "temp1"

            test_template_two = TemplateOutputFile(
                output_directory=temp_directory,
                template_name="myOtherTemplate.test",
                content="This is the other sample content in my template",
                overwrite=True
            )
            test_template_two.file_name = "temp2"

            templates = [test_template_one, test_template_two]

            write_generated_templates_to_file(templates)
            temp_directory_files = os.listdir(temp_directory)

            self.assertEqual(len(templates), len(temp_directory_files))

            for i in range(len(templates)):
                expected_template = templates[i]

                self.assertIn(expected_template.file_name, temp_directory_files)

                with open(os.path.join(temp_directory, expected_template.file_name)) as file:
                    self.assertEqual(expected_template.content, file.read())

    def test_write_generated_templates_to_file_in_directory(self):
        with TemporaryDirectory() as temp_dir:
            test_template = TemplateOutputFile(
                output_directory=os.path.join(temp_dir, "tests"),
                template_name="template.test",
                content="The sample content.",
                overwrite=False
            )
            test_template.file_name = "temp"

            self.assertIsNotNone(test_template)
            self.assertEqual(test_template.file_name, "temp")
            self.assertEqual(test_template.output_directory, "tests")

            write_generated_templates_to_file([test_template])
            temp_dir_files = os.listdir(temp_dir)

            self.assertEqual(len(temp_dir_files), 1)
            self.assertIn(test_template.output_directory, temp_dir_files)

            test_file = os.path.join(temp_dir, test_template.output_directory, test_template.file_name)
            with open(test_file) as file:
                self.assertEqual(test_template.content, file.read())

    def test_does_not_overwrite_existing_file_with_overwrite_false(self):
        content = "original content"
        new_content = "new content"
        with TemporaryDirectory() as temp_dir, temporary_test_file(content, dir=temp_dir) as test_file:
            test_template = TemplateOutputFile(
                output_directory=temp_dir,
                template_name="test-template",
                content=new_content,
                overwrite=False
            )

            test_template.file_name = test_file.name

            self.assertFalse(test_template.overwrite)

            write_generated_templates_to_file([test_template])

            with open(test_file.name) as file:
                self.assertNotEqual(file.read(), new_content)
