from unittest import TestCase
from unittest.mock import patch

from aac.lang.server import default_host, default_port, start_lsp


class TestLspServer(TestCase):
    @patch("aac.lang.server.server")
    def test_starts_tcp_server_with_default_host_and_port(self, server):
        result = start_lsp(dev=True)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_tcp.called_with(default_host, default_port))

    @patch("aac.lang.server.server")
    def test_starts_tcp_server_with_custom_host_and_port(self, server):
        host, port = "host", 123
        result = start_lsp(host, port, True)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_tcp.called_with(host, port))

    @patch("aac.lang.server.server")
    def test_starts_io_server_when_not_in_dev_mode(self, server):
        result = start_lsp(dev=False)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_io.called)
