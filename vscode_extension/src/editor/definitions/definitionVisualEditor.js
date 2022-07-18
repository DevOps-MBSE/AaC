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
            console.log(data)
            var editor = new JSONEditor(document.getElementById('main'),
                {
                schema: {
                type: "object",
                title: data.name,
                properties: {
                    make: {
                    type: "string",
                    enum: [
                        "Toyota",
                        "BMW",
                        "Honda",
                        "Ford",
                        "Chevy",
                        "VW"
                    ]
                    },
                    model: {
                    type: "string"
                    },
                    year: {
                    type: "integer",
                    enum: [
                        1995,1996,1997,1998,1999,
                        2000,2001,2002,2003,2004,
                        2005,2006,2007,2008,2009,
                        2010,2011,2012,2013,2014
                    ],
                    default: 2008
                    },
                    safety: {
                    type: "integer",
                    format: "rating",
                    maximum: "5",
                    exclusiveMaximum: false,
                    readonly: false
                    }
                }
                }
            });

            // Hook up the submit button to log to the console
            document.getElementById('submit').addEventListener('click',function() {
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