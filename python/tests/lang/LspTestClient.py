"""An LSP client used for testing the Architecture-as-Code LSP server."""

import os
import asyncio

from threading import Thread

from pygls.lsp import methods
from pygls.lsp.types import Model
from pygls.server import LanguageServer

from aac.lang.server import setup_features


default_timeout = 3


class LspTestClient:
    """An AaC LSP test client.

    The test client handles starting a test instance of the AaC LSP server and communicating with it.

    Attributes:
        server (LanguageServer): A test version of the AaC LSP server.
        client (LanguageServer): The client used for communicating with the AaC LSP server.
    """

    def __init__(self):
        """Create an LSP test client."""
        client_server_reader, client_server_writer = os.pipe()
        server_client_reader, server_client_writer = os.pipe()

        self.server, self._server_thread = self._configure_ls(client_server_reader, server_client_writer)
        self.client, self._client_thread = self._configure_ls(server_client_reader, client_server_writer)

    def _configure_ls(self, reader: int, writer: int):
        """Create, configure, and return a new LanguageServer and it's associated thread.

        Args:
            reader (int): The file descriptor used for reading standard input.
            writer (int): The file descriptor used for writing standard output.

        Returns:
            The newly created LanguageServer and it's associated thread.
        """
        ls = LanguageServer(asyncio.new_event_loop())
        thread = Thread(target=ls.start_io, args=(os.fdopen(reader, "rb"), os.fdopen(writer, "wb")))
        thread.daemon = True
        return ls, thread

    def start(self):
        """Start the test LSP server and client."""
        self._server_thread.start()
        self.server.thread_id = self._server_thread.ident
        setup_features(self.server)

        self._client_thread.start()

    def stop(self):
        """Stop the test LSP server and client."""
        shutdown_response = self.send_request(methods.SHUTDOWN).result(timeout=default_timeout)
        assert shutdown_response is None

        self.send_notification(methods.EXIT)
        self._server_thread.join()

        self.client._stop_event.set()
        try:
            self.client.loop._signal_handlers.clear()
        except AttributeError:
            pass
        self._client_thread.join()

    def send_request(self, method: str, params: Model = None, timeout: int = default_timeout):
        """Send a request to the server.

        Args:
            method (str): The LSP method to use for the request.
            params (Model): The parameters to send with the request. (optional)
            timeout (int): The timeout to use when waiting for a result. If not passed,
                           default_timeout is used.

        Returns:
            The LSP response for the sent request.
        """
        if params:
            return self.client.lsp.send_request(method, params).result(timeout=timeout)
        return self.client.lsp.send_request(method)

    def send_notification(self, method: str):
        """Send a notification to the server.

        Args:
            method (str): The LSP method to use for the notification.

        Returns:
            The LSP response for the sent notification.
        """
        return self.client.lsp.notify(method)
