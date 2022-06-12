from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context


class BaseTestCase(TestCase):
    """Base test case that performs common setup/teardown including ensuring a fresh language context."""

    def setUp(self) -> None:
        super().setUp()
        get_active_context(reload_context=True)
