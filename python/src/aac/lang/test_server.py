"""Test the LSP server."""

import requests
from pygls.lsp.types import ClientCapabilities, InitializedParams, InitializeParams

identifier = 0


async def _request(method, params, host="http://127.0.0.1", port=9528):
    global identifier

    identifier += 1
    headers = {"Content-Type": "application/jsonrpc-vscode; charset=utf8"}
    body = f"""{{
        "jsonrpc": "2.0",
        "id": {identifier},
        "method": "{method}",
        "params": {params.json()}
    }}"""
    return await requests.get(url=f"{host}:{port}", data=body, headers=headers)


async def _initialize():
    global identifier

    params = InitializeParams(
        process_id=68834,
        capabilities=ClientCapabilities(),
        client_info={"name": "aac-client"},
        trace="verbose",
    )
    return await _request("initialize", params)


async def _initialized():
    global identifier

    params = InitializedParams()
    return await _request("initialized", params)
