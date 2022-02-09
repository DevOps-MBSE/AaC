"""Test the LSP server."""

import requests
from pygls.lsp.types import (
    ClientCapabilities,
    InitializedParams,
    InitializeParams,
    HoverParams,
    TextDocumentIdentifier,
    Position,
)

from server import default_host, default_port

identifier = 0


def _request(method, params, host=default_host, port=default_port):
    global identifier

    identifier += 1
    headers = {"Content-Type": "application/jsonrpc-vscode; charset=utf8"}
    body = f"""{{
        "jsonrpc": "2.0",
        "id": {identifier},
        "method": "{method}",
        "params": {params.json()}
    }}"""
    return requests.post(url=f"http://{host}:{port}", json=body, headers=headers)


def _initialize():
    params = InitializeParams(
        capabilities=ClientCapabilities(),
        client_info={"name": "aac-client"},
        trace="verbose",
    )
    return _request("initialize", params)


def _initialized():
    params = InitializedParams()
    return _request("initialized", params)


def _hover():
    params = HoverParams(
        textDocument=TextDocumentIdentifier(uri="file:///test.yaml"),
        position=Position(line=5, character=10),
    )
    return _request("textDocument/hover", params)
