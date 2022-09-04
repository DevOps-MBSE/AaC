"""An LSP client used for testing the Architecture-as-Code LSP server."""

import os
import asyncio

from asyncio.tasks import sleep
from threading import Thread
from typing import Optional

from pygls.lsp import methods
from pygls.lsp.types import Model

from aac.plugins.lsp_server.language_server import AacLanguageServer


# We have to sleep to give the server enough time to finish processing changes to the active
# context, etc. Just awaiting the send_request function isn't enough since the request will get
# sent and return.
SLEEP_TIME = 1
DEFAULT_TIMEOUT_IN_SECONDS = 3


class LspTestClient:
    """An AaC LSP test client.

    The test client handles starting a test instance of the AaC LSP server and communicating with it.

    Attributes:
        aac_language_server (AacLanguageServer): The AaC server mana
        server (AacLanguageServer): A test version of the AaC LSP server.
        client (LanguageServer): The client used for communicating with the AaC LSP server.
    """

    def __init__(self):
        """Create an LSP test client."""
        client_server_reader, client_server_writer = os.pipe()
        server_client_reader, server_client_writer = os.pipe()

        self.server, self._server_thread = self._configure_ls(client_server_reader, server_client_writer)
        self.client, self._client_thread = self._configure_ls(server_client_reader, client_server_writer)

    def _configure_ls(self, reader: int, writer: int):
        """
        Create, configure, and return a new LanguageServer and it's associated thread.

        Args:
            reader (int): The file descriptor used for reading standard input.
            writer (int): The file descriptor used for writing standard output.

        Returns:
            The newly created LanguageServer and it's associated thread.
        """
        ls = AacLanguageServer(loop=asyncio.new_event_loop())
        thread = Thread(target=ls.start_io, args=(os.fdopen(reader, "rb"), os.fdopen(writer, "wb")))
        thread.daemon = True
        return ls, thread

    async def start(self):
        """Start the test LSP server and client."""
        self._server_thread.start()
        self.server.thread_id = self._server_thread.ident
        self._client_thread.start()

    async def stop(self):
        """Stop the test LSP server and client."""
        shutdown_response = (await self.send_request(methods.SHUTDOWN)).result(timeout=DEFAULT_TIMEOUT_IN_SECONDS)
        assert shutdown_response is None

        await self.send_notification(methods.EXIT)
        self._server_thread.join()

        self.client._stop_event.set()
        try:
            self.client.loop._signal_handlers.clear()
        except AttributeError:
            pass
        self._client_thread.join()

    async def send_request(self, method: str, params: Optional[Model] = None):
        """
        Send a request to the server.

        Args:
            method (str): The LSP method to use for the request.
            params (Model): The parameters to send with the request. (optional)

        Returns:
            The LSP response for the sent request.
        """
        response = self.client.lsp.send_request(method, params)
        await sleep(SLEEP_TIME)
        return response

    async def send_notification(self, method: str, params: Optional[Model] = None) -> None:
        """
        Send a notification to the server.

        Args:
            method (str): The LSP method to use for the notification.
            params (Optional[Model]): Optional parameters to send with the notification.
        """
        self.client.send_notification(method, params)
        await sleep(SLEEP_TIME)
