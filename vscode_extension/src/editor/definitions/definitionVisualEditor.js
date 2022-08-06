/* tslint:disable */
/* eslint-disable */

// This script is run within the webview itself
(function () {
    // @ts-ignore
    const vscode = acquireVsCodeApi();

    class DefinitionEditor {
        constructor( /** @type {HTMLElement} */ parent) {
            this.ready = false;

            this.editable = false;
            this.container = parent
        }

        async setEditorData(data) {
            // Initialize the editor with a JSON schema
            const root_key = Object.keys(data.structure)[0];
            var editor = new JSONEditor(document.getElementById('main'),
                {
                    "use_default_values": true,
                    "prompt_before_delete": false,
                    "disable_collapse": true,
                    "disable_array_delete_last_row": true,
                    "array_controls_top": true,
                    "schema": data.jsonSchema,
                    "startval": data.structure[root_key]
                }
            );

            // Hook up the submit button to log to the console
            document.getElementById('submit').addEventListener('click', function () {
                // Get the value from the editor
                console.log(editor.getValue());
            });
        }
    }

    const editor = new DefinitionEditor(document.querySelector('#main'));

    // Handle messages from the extension
    window.addEventListener('message', async event => {
        const { type, body, requestId } = event.data;
        switch (type) {
            case 'update':
                {
                    await editor.setEditorData(body.value)
                    return;
                }
        }
    });

    // Signal to VS Code that the webview is initialized.
    vscode.postMessage({ type: 'ready' });
}());
