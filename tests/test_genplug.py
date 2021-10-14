from unittest import TestCase

from aac import template_engine


class TestTemplateEngine(TestCase):
    def test_load_templates(self):
        templates = template_engine.load_templates("genplug")
        print(templates)
        self.assertGreater(len(templates), 0)
