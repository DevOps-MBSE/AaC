from unittest import TestCase

from aac import parser


class TestArchParser(TestCase):

    def test_nothing(self):
        self.assertTrue(True)

    # TODO  For now I'm just going to test those items that don't require file system manipulation.  Expand later.

    # def test_process_data_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "data": {
    #             "fields": [
    #                 {"type": "string", "name": "name"},
    #                 {"type": "Field[]", "name": "fields"},
    #                 {"type": "string[]", "name": "required"},
    #             ],
    #             "required": ["name", "fields"],
    #             "name": "data",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(data_types), 1)

    # def test_process_model_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "model": {
    #             "name": "EchoService",
    #             "behavior": [
    #                 {
    #                     "name": "echo",
    #                     "input": [{"type": "Message", "name": "inbound"}],
    #                     "output": [{"type": "Message", "name": "outbound"}],
    #                     "acceptance": [
    #                         {
    #                             "then": ["The user receives the same message from EchoService."],
    #                             "given": ["The EchoService is running."],
    #                             "when": ["The user sends a message to EchoService."],
    #                             "scenario": "onReceive",
    #                         }
    #                     ],
    #                     "type": "request-response",
    #                     "description": "This is the one thing it does.",
    #                 }
    #             ],
    #             "description": "This is a message mirror.",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(model_types), 1)

    # def test_process_enum_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "enum": {
    #             "values": ["string", "int", "number", "bool", "date", "file"],
    #             "name": "Primitives",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(enum_types), 1)

    # def test_process_use_case_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "usecase": {
    #             "participants": [
    #                 {"type": "~User", "name": "user"},
    #                 {"type": "System", "name": "system"},
    #             ],
    #             "steps": [
    #                 {
    #                     "action": "doFlow",
    #                     "source": "user",
    #                     "step": "The user invokes doFlow on system.",
    #                     "target": "system",
    #                 },
    #                 {
    #                     "action": "response",
    #                     "source": "system",
    #                     "step": "The system performs flow and responds to the user.",
    #                     "target": "user",
    #                 },
    #             ],
    #             "description": "Something happens.",
    #             "title": "Nominal flow of data through the system.",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(use_case_types), 1)

    # def test_process_ext_enum_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "extension": {
    #             "enumExt": {"add": ["rest"]},
    #             "type": "BehaviorType",
    #             "name": "restActionType",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(ext_types), 1)

    # def test_process_ext_data_root(self):
    #     model_types = {}
    #     data_types = {}
    #     enum_types = {}
    #     use_case_types = {}
    #     ext_types = {}

    #     root = {
    #         "extension": {
    #             "dataExt": {"add": [{"name": "errCount", "type": "int"}]},
    #             "name": "addCountToValidationResult",
    #             "type": "ValidationResult",
    #         }
    #     }

    #     parser._process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)
    #     self.assertEqual(len(ext_types), 1)
