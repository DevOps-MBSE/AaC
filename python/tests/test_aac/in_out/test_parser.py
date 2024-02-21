from os.path import basename, sep, isfile
from os import linesep
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import TestCase
import tempfile

from aac.in_out.constants import AAC_DOCUMENT_EXTENSION, YAML_DOCUMENT_SEPARATOR
from aac.in_out.parser import parse, ParserError
from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation

PARSER_TEST_SOURCE = "<parser test>"


class TestParser(TestCase):

    def create_test_file(self, path: str, content: str) -> str:
        with open(path, "w") as test_file:
            test_file.write(content)
        return path
    
    def get_lexeme_values_for_definition(self, name: str, definitions: list[Definition]) -> list[str]:
        lexemes = [definition.lexemes for definition in definitions if definition.name == name][0]
        return [lexeme.value for lexeme in lexemes]

    def check_definition(self, definition: Optional[Definition], name: str, type: str):
        self.assertIsNotNone(definition)
        self.assertEqual(type, definition.get_root_key())
        self.assertEqual(name, definition.name)

    def check_parser_errors(self, filespec: str, *error_messages: list[str]):
        with self.assertRaises(ParserError) as cm:
            parse(filespec)

        # Assert that each error message is contained in the returned error message string.
        errors = sep.join(cm.exception.errors)
        list(map(lambda e: self.assertIn(e, errors), error_messages))
        self.assertEqual(cm.exception.source, filespec)

    def test_can_get_lexemes_from_parsed_architecture_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", TEST_MESSAGE_CONTENTS.strip())
            parsed_definitions = parse(test_yaml)
            self.assertEqual(1, len(parsed_definitions))
            parsed_definition = parsed_definitions[0]

            self.assertGreaterEqual(len(parsed_definition.lexemes), 2)

            first, second, *_ = parsed_definition.lexemes
            self.assertEqual(first.source, test_yaml)
            self.assertEqual(first.value, "schema")
            self.assertEqual(first.location, SourceLocation(0, 0, 0, 6))

            self.assertEqual(second.source, test_yaml)
            self.assertEqual(second.value, "name")
            self.assertEqual(second.location, SourceLocation(1, 2, 10, 4))

    def test_errors_when_parsing_invalid_yaml(self):
        content = "model: ]["
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", content)
            self.check_parser_errors(test_yaml, "invalid YAML")

    def test_errors_when_parsing_incomplete_model(self):
        content = "model:"
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", content)
            self.check_parser_errors(test_yaml, "Definition is missing field 'name'", content)

    def test_errors_when_parsing_non_yaml(self):
        content = "not yaml"
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", content)
            self.check_parser_errors(test_yaml, "not YAML", content)

    def test_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        parsed_definitions = parse(content, source_uri=PARSER_TEST_SOURCE)

        self.assertEqual(len(parsed_definitions), 2)

        contents = [definition.content for definition in parsed_definitions]
        self.assertIn(TEST_MESSAGE_CONTENTS, contents)
        self.assertIn(f"{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", contents)

    def test_file_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", content)
            parsed_definitions = parse(test_yaml)

            self.assertEqual(len(parsed_definitions), 2)

            contents = [definition.content for definition in parsed_definitions]
            self.assertIn(TEST_MESSAGE_CONTENTS, contents)
            self.assertIn(f"{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", contents)

    def test_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        parsed_definitions = parse(content, source_uri=PARSER_TEST_SOURCE)

        self.assertEqual(len(parsed_definitions), 2)

        self.assertNotIn(
            TEST_STATUS_NAME,
            self.get_lexeme_values_for_definition(TEST_MESSAGE_NAME, parsed_definitions),
        )
        self.assertNotIn(
            TEST_MESSAGE_NAME,
            self.get_lexeme_values_for_definition(TEST_STATUS_NAME, parsed_definitions),
        )

    def test_file_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        with tempfile.TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.aac", content)
            parsed_definitions = parse(test_yaml)

            self.assertEqual(len(parsed_definitions), 2)

            self.assertNotIn(
                TEST_STATUS_NAME,
                self.get_lexeme_values_for_definition(TEST_MESSAGE_NAME, parsed_definitions),
            )
            self.assertNotIn(
                TEST_MESSAGE_NAME,
                self.get_lexeme_values_for_definition(TEST_STATUS_NAME, parsed_definitions),
            )

    def test_does_not_add_doc_separator_if_not_already_present(self):
        definition, *_ = parse(TEST_MESSAGE_CONTENTS, source_uri=PARSER_TEST_SOURCE)
        self.assertEqual(definition.content, TEST_MESSAGE_CONTENTS)

        definitions = parse(
            f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", source_uri=PARSER_TEST_SOURCE
        )

        message_definition, *_ = [definition for definition in definitions if definition.name == TEST_MESSAGE_NAME]
        self.assertFalse(message_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))

        status_definition, *_ = [definition for definition in definitions if definition.name == TEST_STATUS_NAME]
        self.assertTrue(status_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))

    def test_no_errors_for_empty_definitions(self):
        definitions = parse(
            f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{linesep}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        )
        self.assertEqual(len(definitions), 2)


class TestParserImports(TestCase):
    """Exercises the import functionality of the parser."""

    def create_test_file(self, path: str, content: str) -> str:
        with open(path, "w") as test_file:
            test_file.write(content)
        return path

    def check_definition(self, definition: Optional[Definition], name: str, type: str):
        self.assertIsNotNone(definition)
        self.assertEqual(type, definition.get_root_key())
        self.assertEqual(name, definition.name)

    def test_can_handle_architecture_file_with_imports(self):
        with TemporaryDirectory() as temp_dir:
            import1 = self.create_test_file(f"{temp_dir}/{TEST_MESSAGE_FILE_NAME}", TEST_MESSAGE_CONTENTS)
            import2 = self.create_test_file(f"{temp_dir}/{TEST_STATUS_FILE_NAME}", TEST_STATUS_CONTENTS)
            test_yaml = self.create_test_file(f"{temp_dir}/test_model.aac", TEST_MODEL_CONTENTS)

            definitions = parse(test_yaml)
            self.assertEqual(len(definitions), 4)

            context = LanguageContext()
            definitions = context.parse_and_load(test_yaml)
            self.assertEqual(len(definitions), 4)

            import_definitions = [definition for definition in definitions if definition.get_root_key() == "import"]
            import_basenames = []
            for imp in import_definitions:
                import_basenames.extend([basename(entry) for entry in imp.instance.files])
            self.assertIn(basename(import1), import_basenames)
            self.assertIn(basename(import2), import_basenames)

            schema_message_definition = context.get_definitions_by_name(TEST_MESSAGE_NAME)[0]
            enum_status_definition = context.get_definitions_by_name(TEST_STATUS_NAME)[0]
            model_echosvc_definition = context.get_definitions_by_name(TEST_MODEL_NAME)[0]

            self.check_definition(schema_message_definition, TEST_MESSAGE_NAME, "schema")
            self.check_definition(enum_status_definition, TEST_STATUS_NAME, "enum")
            self.check_definition(model_echosvc_definition, TEST_MODEL_NAME, "model")

            self.assertEqual(schema_message_definition.source.uri, import1)
            self.assertEqual(enum_status_definition.source.uri, import2)
            self.assertEqual(model_echosvc_definition.source.uri, test_yaml)

            first_import, *_ = [definition for definition in definitions if definition.get_root_key() == "import"]
            first, _, third, *_ = first_import.lexemes
            self.assertEqual(first.source, test_yaml)
            self.assertEqual(first.value, "import")
            self.assertEqual(first.location, SourceLocation(1, 0, 1, 6))

            self.assertEqual(third.source, test_yaml)
            self.assertEqual(third.value, f"./{TEST_MESSAGE_FILE_NAME}")
            self.assertEqual(third.location, SourceLocation(3, 6, 24, 2 + len(TEST_MESSAGE_FILE_NAME)))

    def test_handles_multiple_import_sections_per_file(self):
        another_definition = """
enum:
    name: TestEnum
    values:
    - a
    - b
    - c
"""
        with TemporaryDirectory() as temp_dir:
            import1 = self.create_test_file(f"{temp_dir}/{TEST_STATUS_FILE_NAME}", another_definition)
            import2 = self.create_test_file(f"{temp_dir}/{TEST_MESSAGE_FILE_NAME}", TEST_MESSAGE_CONTENTS)
            import3 = self.create_test_file(f"{temp_dir}/{TEST_STATUS_FILE_NAME}", TEST_STATUS_CONTENTS)
            
            another_import_definition = f"""
import:
  files:
    - {import1}
"""
            content = f"{another_import_definition}{YAML_DOCUMENT_SEPARATOR}{TEST_MODEL_CONTENTS}"
            main = self.create_test_file(f"{temp_dir}/echo_service.aac", content)
            context = LanguageContext()
            definitions = context.parse_and_load(main)
            self.assertEqual(len(definitions), 5)

            import_def_1, import_def_2, *_ = [definition for definition in definitions if definition.get_root_key() == "import"]
            import_basenames = [basename(imp) for imp in import_def_1.instance.files + import_def_2.instance.files]
            self.assertIn(basename(import1), import_basenames)
            self.assertIn(basename(import2), import_basenames)
            self.assertIn(basename(import3), import_basenames)

    def test_parsed_file_imports_non_existent_file(self):
        non_existent_import_definition = """
import:
  files:
    - non_existent_file.aac
"""
        test_message_contents_with_bad_import = YAML_DOCUMENT_SEPARATOR.join([non_existent_import_definition, TEST_MESSAGE_CONTENTS])
        with TemporaryDirectory() as temp_dir:
            initial_file = self.create_test_file(f"{temp_dir}/{TEST_MESSAGE_FILE_NAME}", test_message_contents_with_bad_import)
            definitions = parse(initial_file)
            import_definitions = [definition for definition in definitions if definition.get_root_key() == "import"]

            """ Asserting that the bad import definition was parsed and that this assertion was allowed to complete without error is the
                assertion that the parse mechanism softly handled the bad import. """
            self.assertEqual(len(import_definitions), 1)

    def test_parsed_file_imports_empty_file(self):
        empty_file_name = "empty_file.aac"
        empty_import_content = """
import:
  files:

"""
        # non_existent_import_definition = create_import_definition([empty_file_name])
        test_message_contents_with_bad_import = YAML_DOCUMENT_SEPARATOR.join([empty_import_content, TEST_MESSAGE_CONTENTS])
        with TemporaryDirectory() as temp_dir:
            initial_file = self.create_test_file(f"{temp_dir}/{TEST_MESSAGE_FILE_NAME}", test_message_contents_with_bad_import)
            empty_file = self.create_test_file(f"{temp_dir}/{empty_file_name}", "")
            
            definitions = parse(initial_file)
            import_definitions = [definition for definition in definitions if definition.get_root_key() == "import"]

            self.assertTrue(isfile(empty_file))

            """ Asserting that the bad import definition was parsed and that this assertion was allowed to complete without error is the
                assertion that the parse mechanism softly handled the bad import. """
            self.assertEqual(len(import_definitions), 1)

    def test_parsed_file_imports_invalid_file(self):
        invalid_yaml_file_name = "invalid_yaml_file.aac"
        imvalid_yaml_file_content = f"""
import:
  files:
    - {invalid_yaml_file_name}
"""
        test_message_contents_with_bad_import = YAML_DOCUMENT_SEPARATOR.join([imvalid_yaml_file_content, TEST_MESSAGE_CONTENTS])
        with TemporaryDirectory() as temp_dir:
            initial_file = self.create_test_file(f"{temp_dir}/{TEST_MESSAGE_FILE_NAME}", test_message_contents_with_bad_import)
            empty_file = self.create_test_file(f"{temp_dir}/{invalid_yaml_file_name}", "")
            definitions = parse(initial_file)
            import_definitions = [definition for definition in definitions if definition.get_root_key() == "import"]

            self.assertTrue(isfile(empty_file))

            """ Asserting that the bad import definition was parsed and that this assertion was allowed to complete without error is the
                assertion that the parse mechanism softly handled the bad import. """
            self.assertEqual(len(import_definitions), 1)


TEST_MODEL_NAME = "EchoService"
TEST_MESSAGE_NAME = "Message"
TEST_STATUS_NAME = "Status"

TEST_MESSAGE_FILE_NAME = f"{TEST_MESSAGE_NAME}{AAC_DOCUMENT_EXTENSION}"
TEST_STATUS_FILE_NAME = f"{TEST_STATUS_NAME}{AAC_DOCUMENT_EXTENSION}"

TEST_MESSAGE_CONTENTS = f"""
schema:
  name: {TEST_MESSAGE_NAME}
  package: test_aac.in_out
  fields:
  - name: body
    type: string
  - name: sender
    type: string
"""
TEST_STATUS_CONTENTS = f"""
enum:
  name: {TEST_STATUS_NAME}
  package: test_aac.in_out
  values:
    - sent
    - 'failed to send'
"""
TEST_MODEL_CONTENTS = f"""
import:
  files:
    - .{sep}{TEST_MESSAGE_FILE_NAME}
    - {TEST_STATUS_FILE_NAME}
---
model:
  name: {TEST_MODEL_NAME}
  description: This is a message mirror.
  behavior:
    - name: echo
      description: This is the one thing it does.
      input:
        - name: inbound
          type: Message
      output:
        - name: outbound
          type: Message
      acceptance:
        - name: this is a test
          scenarios: 
          - name: onReceive
            given:
            - The EchoService is running.
            when:
                - The user sends a message to EchoService.
            then:
                - The user receives the same message from EchoService.
"""
