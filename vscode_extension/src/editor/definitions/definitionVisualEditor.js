/* tslint:disable */
const vscode = acquireVsCodeApi();

const AacEditorEventTypes = {
	READY: 1,
    EDIT: 2,
    SAVE: 3
}

// This script is run within the webview itself
(function () {
    class DefinitionEditor {
        constructor( /** @type {HTMLElement} */ parent) {
            this.ready = false;

            this.editable = false;
            this.container = parent;
            this.rootKey = "";
            this.sourceUri = "";
            this.editor = null;
        }

        async setEditorData(data) {
            // Initialize the editor with a JSON schema
            this.rootKey = Object.keys(data.structure)[0];
            addTitlesToJsonSchema(data.jsonSchema, this.rootKey)

            if (this.editor) {
                this.editor.destroy();
            }

            this.editor = new JSONEditor(document.getElementById('main'),
                {
                    "use_default_values": true,
                    "prompt_before_delete": false,
                    "disable_collapse": false,
                    "disable_array_delete_last_row": true,
                    "array_controls_top": true,
                    "disable_edit_json": true,
                    "schema": data.jsonSchema,
                    "startval": data.structure[this.rootKey]
                }
            );

            this.editor.on('change', () => {
                const editorContent = this.editor?.getValue()
                const rootKey = editor.rootKey
                const definitionStructure = {}
                definitionStructure[rootKey] = editorContent

                const aacDefinitionEdit = {
                    name: definitionStructure[rootKey].name,
                    sourceUri: this.sourceUri,
                    structure: definitionStructure
                };

                vscode.postMessage({ type: AacEditorEventTypes.EDIT, body: aacDefinitionEdit});
            });

            // Hook up the submit button to log to the console
            document.getElementById('submit').addEventListener('click', function () {
                vscode.postMessage({ type: AacEditorEventTypes.SAVE });
            });
        }
    }

    const editor = new DefinitionEditor(document.querySelector('#main'));

    // Handle messages from the extension
    window.addEventListener('message', async event => {
        const { type, body } = event.data;
        switch (type) {
            case AacEditorEventTypes.EDIT:
                {
                    await editor.setEditorData(body)
                    return;
                }
        }
    });

    // Send editor is ready message
    vscode.postMessage({ type: AacEditorEventTypes.READY });
}());

function addTitlesToJsonSchema(jsonSchema, definitionRootKey) {
    jsonSchema.title = definitionRootKey

    recursivelyApplyArrayElementTitles(jsonSchema.properties)
}

function recursivelyApplyArrayElementTitles(array_properties_object) {
    if (array_properties_object) {
        Object.entries(array_properties_object).forEach(function (entry) {
            const key = entry[0]
            const value = entry[1]
            if (value.type == "array") {
                entry_title = getArrayEntryTitleFromArrayName(key)
                array_properties_object[key].items.title = entry_title
                name_template = (array_properties_object[key].items.properties?.name !== undefined ? "- {{ self.name }}" : "")

                array_properties_object[key].items.headerTemplate = `${entry_title} {{ i1 }} ${name_template}`
                recursivelyApplyArrayElementTitles(array_properties_object[key].items.properties)
            }
        });
    }
}

function getArrayEntryTitleFromArrayName(array_name) {
    return (array_name.endsWith("s") ? array_name.slice(0, -1) : array_name)
}
