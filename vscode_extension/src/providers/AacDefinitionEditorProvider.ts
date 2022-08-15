import * as path from 'path'
import * as vscode from 'vscode';
import { disposeAll } from '../disposable';
import { AacDefinitionsDocument, AacDefinitionEdit } from '../editor/definitions/DefinitionsDocument'
import { getNonce } from '../nonce';
import { aacRestApi, DefinitionModel } from '../requests/aacRequests'

/**
 * Provider for AaC visual definition editors.
 *
 * AaC visual definition editors allow users to visually interact with the AaC REST API and definitions. There is no real underlying file for these editors as multiple definitions can exist in a file.
 */
export class AacDefinitionEditorProvider implements vscode.CustomEditorProvider<AacDefinitionsDocument> {

    public static register(context: vscode.ExtensionContext): vscode.Disposable {
        return vscode.window.registerCustomEditorProvider(
            AacDefinitionEditorProvider.viewType,
            new AacDefinitionEditorProvider(context),
            {
                webviewOptions: {
                    retainContextWhenHidden: true, //keeps the webview alive even when it is not visible. Does have a memory overhead.
                },
                supportsMultipleEditorsPerDocument: false,
            });
    }

    private static readonly viewType = 'aac.visualEditor';

    /**
     * Tracks all known webviews
     */
    private readonly webviews = new WebviewCollection();

    constructor(
        private readonly _context: vscode.ExtensionContext
    ) { }

    //#region CustomEditorProvider

    async openCustomDocument(
        uri: vscode.Uri,
        openContext: { backupId?: string },
        _token: vscode.CancellationToken
    ): Promise<AacDefinitionsDocument> {
        const document: AacDefinitionsDocument = await AacDefinitionsDocument.create(uri, openContext.backupId, {
            getFileData: async () => {
                const webviewsForDocument = Array.from(this.webviews.get(document.uri));
                if (!webviewsForDocument.length) {
                    throw new Error('Could not find webview to save for');
                }
                const panel = webviewsForDocument[0];
                return new Uint8Array()
            }
        });

        const listeners: vscode.Disposable[] = [];

        listeners.push(document.onDidChange(event => {
            // Propagate document changes to VS Code.
            this._onDidChangeCustomDocument.fire({
                document,
                ...event,
            });
        }));

        listeners.push(document.onDidChangeContent(event => {
            for (const webviewPanel of this.webviews.get(document.uri)) {
                this.postMessage(webviewPanel, 'update', {
                    edits: event.edits,
                    content: event.content,
                });
            }
        }));

        document.onDidDispose(() => disposeAll(listeners));

        return document;
    }

    async resolveCustomEditor(
        document: AacDefinitionsDocument,
        webviewPanel: vscode.WebviewPanel,
        _token: vscode.CancellationToken
    ): Promise<void> {
        // Add the webview to the internal set of active webviews
        this.webviews.add(document.uri, webviewPanel);

        // Setup initial content for the webview
        webviewPanel.webview.options = {
            enableScripts: true,
        };
        webviewPanel.webview.html = this.getHtmlForWebview(webviewPanel.webview);

        webviewPanel.webview.onDidReceiveMessage(event => this.onMessage(document, event));

        // Wait for the webview to be properly ready before we init
        webviewPanel.webview.onDidReceiveMessage(event => {
            if (event.type === 'ready') {
                this.getDefinition(path.basename(document.uri.fsPath), true).then(response => {
                    this.postMessage(webviewPanel, 'update', {
                        value: response.body
                    });
                })
            }
        });
    }

    private readonly _onDidChangeCustomDocument = new vscode.EventEmitter<vscode.CustomDocumentEditEvent<AacDefinitionsDocument>>();
    public readonly onDidChangeCustomDocument = this._onDidChangeCustomDocument.event;

    public saveCustomDocument(document: AacDefinitionsDocument, cancellation: vscode.CancellationToken): Thenable<void> {
        return document.save(cancellation);
    }

    public saveCustomDocumentAs(document: AacDefinitionsDocument, destination: vscode.Uri, cancellation: vscode.CancellationToken): Thenable<void> {
        return document.saveAs(destination, cancellation);
    }

    public revertCustomDocument(document: AacDefinitionsDocument, cancellation: vscode.CancellationToken): Thenable<void> {
        return document.revert(cancellation);
    }

    public backupCustomDocument(document: AacDefinitionsDocument, context: vscode.CustomDocumentBackupContext, cancellation: vscode.CancellationToken): Thenable<vscode.CustomDocumentBackup> {
        return document.backup(context.destination, cancellation);
    }

    //#endregion

    /**
     * Get the editor webview HTML.
     */
    private getHtmlForWebview(webview: vscode.Webview): string {
        // Local path to script and css for the webview
        const editorSourceDirPath = path.join(this._context.extensionUri.fsPath, 'src', 'editor', 'definitions')

        const scriptUri = webview.asWebviewUri(vscode.Uri.parse(path.join(editorSourceDirPath, 'definitionVisualEditor.js')));
        const styleMainUri = webview.asWebviewUri(vscode.Uri.parse(path.join(editorSourceDirPath, 'definitionEditor.css')));

        const jsonNodeModulesPath = path.join(this._context.extensionUri.fsPath, 'node_modules')

        const jsonEditorPath = vscode.Uri.parse(path.join(jsonNodeModulesPath, '@json-editor', 'json-editor', 'dist', 'jsoneditor.js'));

        const jsonEditorScriptUri = webview.asWebviewUri(jsonEditorPath);


        // Use a nonce to whitelist which scripts can be run
        const nonce = getNonce();

        return /* html */`
			<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">

				<!--
				Use a content security policy to only allow loading images from https or from our extension directory,
				and only allow scripts that have a specific nonce.
				-->
				<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${webview.cspSource} blob:; style-src ${webview.cspSource} 'unsafe-inline'; script-src * data: ${webview.cspSource} 'unsafe-inline' 'unsafe-eval';">

				<meta name="viewport" content="width=device-width, initial-scale=1.0">

				<link href="${styleMainUri}" rel="stylesheet" />

                <script src="${jsonEditorScriptUri}" http-equiv="Content-Security-Policy" script-src-elem "${jsonEditorScriptUri}" nonce="${nonce}";></script>
				<title></title>
			</head>
			<body>
				<div id="main"></div>
                <button id='submit'>Save</button>
                <script src="${scriptUri}" http-equiv="Content-Security-Policy" script-src-elem 'unsafe-inline' ${scriptUri} nonce='${nonce}';></script>
			</body>
			</html>`;
    }

    private readonly _callbacks = new Map<number, (response: any) => void>();

    private postMessage(panel: vscode.WebviewPanel, type: string, body: any): void {
        panel.webview.postMessage({ type, body });
    }

    private onMessage(document: AacDefinitionsDocument, message: any) {
        console.log(document)

        switch (message.type) {
            case 'save':
                console.log(message.body as AacDefinitionEdit)

                const updatedDefinitionModel = new DefinitionModel()
                updatedDefinitionModel.name = message.body.name
                updatedDefinitionModel.structure = message.body
                updatedDefinitionModel.sourceUri = "test"

                console.log(updatedDefinitionModel)
                this.updateDefinition(updatedDefinitionModel)
                return;
        }
    }

    private getDefinition(definitionName: string, includeJsonSchema: boolean = false) {
        return Promise.resolve(aacRestApi.getDefinitionByNameDefinitionGet(definitionName, includeJsonSchema)).catch(error => {console.error(error)})
    }

    private updateDefinition(definition: DefinitionModel) {
        return Promise.resolve(aacRestApi.updateDefinitionDefinitionPut(definition)).catch(error => {console.error(error)})
    }
}

/**
 * Tracks all webviews.
 */
class WebviewCollection {

    private readonly _webviews = new Set<{
        readonly resource: string;
        readonly webviewPanel: vscode.WebviewPanel;
    }>();

    /**
     * Get all known webviews for a given uri.
     */
    public *get(uri: vscode.Uri): Iterable<vscode.WebviewPanel> {
        const key = uri.toString();
        for (const entry of this._webviews) {
            if (entry.resource === key) {
                yield entry.webviewPanel;
            }
        }
    }

    /**
     * Add a new webview to the collection.
     */
    public add(uri: vscode.Uri, webviewPanel: vscode.WebviewPanel) {
        const entry = { resource: uri.toString(), webviewPanel };
        this._webviews.add(entry);

        webviewPanel.onDidDispose(() => {
            this._webviews.delete(entry);
        });
    }
}

