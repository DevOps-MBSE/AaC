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
            const rootKey = Object.keys(data.structure)[0];
            add_titles_to_json_schema(data.jsonSchema, rootKey)
            var editor = new JSONEditor(document.getElementById('main'),
                {
                    "use_default_values": true,
                    "prompt_before_delete": false,
                    "disable_collapse": false,
                    "disable_array_delete_last_row": true,
                    "array_controls_top": true,
                    "disable_edit_json": true,
                    "schema": data.jsonSchema,
                    "startval": data.structure[rootKey]
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

function add_titles_to_json_schema(jsonSchema, definitionRootKey) {
    jsonSchema.title = definitionRootKey

    recursively_apply_array_element_titles(jsonSchema.properties)
}

function recursively_apply_array_element_titles(array_properties_object) {
    if (array_properties_object) {
        Object.entries(array_properties_object).forEach(function (entry) {
            const key = entry[0]
            const value = entry[1]
            if (value.type == "array") {
                console.log(`boom ${entry}`)
                entry_title = get_array_entry_title_from_array_name(key)
                array_properties_object[key].items.title = entry_title
                name_template = (array_properties_object[key].items.properties?.name !== undefined ? "- {{ self.name }}" : "")

                array_properties_object[key].items.headerTemplate = `${entry_title} {{ i1 }} ${name_template}`
                recursively_apply_array_element_titles(array_properties_object[key].items.properties)
            }
        });
    }
}

function get_array_entry_title_from_array_name(array_name) {
    return (array_name.endsWith("s") ? array_name.slice(0, -1) : array_name)
}