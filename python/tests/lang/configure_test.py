import os
import asyncio

from threading import Thread

from pygls.lsp import methods
from pygls.server import LanguageServer

from aac.lang.server import setup_features


default_timeout = 3


class LspTestClient:
    def __init__(self):
        """Create an LSP test client."""
        client_server_reader, client_server_writer = os.pipe()
        server_client_reader, server_client_writer = os.pipe()

        self._setup_server(client_server_reader, server_client_writer)
        self._setup_client(server_client_reader, client_server_writer)

    def _setup_server(self, reader, writer):
        self.server = LanguageServer(asyncio.new_event_loop())
        self.server_thread = Thread(target=self.server.start_io, args=(os.fdopen(reader, "rb"), os.fdopen(writer, "wb")))
        self.server_thread.daemon = True

    def _setup_client(self, reader, writer):
        self.client = LanguageServer(asyncio.new_event_loop())
        self.client_thread = Thread(target=self.client.start_io, args=(os.fdopen(reader, "rb"), os.fdopen(writer, "wb")))
        self.client_thread.daemon = True

    def start(self):
        self.server_thread.start()
        self.server.thread_id = self.server_thread.ident
        setup_features(self.server)

        self.client_thread.start()

    def stop(self):
        shutdown_response = self.client.lsp.send_request(methods.SHUTDOWN).result(timeout=default_timeout)
        assert shutdown_response is None

        self.client.lsp.notify(methods.EXIT)
        self.server_thread.join()

        self.client._stop_event.set()
        try:
            self.client.loop._signal_handlers.clear()
        except AttributeError:
            pass
        self.client_thread.join()
