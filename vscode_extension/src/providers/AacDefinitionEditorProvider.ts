import * as path from 'path';
import * as vscode from 'vscode';
import { URI } from 'vscode-uri';
import { disposeAll } from '../disposable';
import { AacDefinitionsDocument, AacDefinitionEdit, AacEditorEventTypes, AacDocumentStateTypes } from '../editor/definitions/DefinitionsDocument';
import { getNonce } from '../nonce';
import { aacRestApi, DefinitionModel, CommandRequestModel } from "../requests/aacRequests";
import { IncomingMessage } from 'http';
import * as queryKeys from './queryKeyConstants'

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
                    retainContextWhenHidden: true, // keeps the webview alive even when it is not visible. Does have a memory overhead.
                },
                supportsMultipleEditorsPerDocument: false,
            });
    }

    private static readonly viewType = 'aac.visualEditor';

    /**
     * Tracks all known webviews
     */
    private readonly webviews = new WebviewCollection();

    constructor(private readonly _context: vscode.ExtensionContext) { }

    async openCustomDocument(
        uri: vscode.Uri,
        _openContext: { backupId?: string },
        _token: vscode.CancellationToken
    ): Promise<AacDefinitionsDocument> {
        const document: AacDefinitionsDocument = await AacDefinitionsDocument.create(uri, {
                getDefinition: this.getDefinition,
                updateDefinition: this.updateDefinition
            });

        const listeners: vscode.Disposable[] = [];
        listeners.push(document.onDidChange(event => {
            // Propagate document changes to VS Code.
            this._onDidChangeCustomDocument.fire({document, ...event});
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

        webviewPanel.webview.onDidReceiveMessage(event => this.onMessage(webviewPanel, document, event));
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

    /**
     * Get the editor webview HTML.
     */
    private getHtmlForWebview(webview: vscode.Webview): string {
        // Local path to script and css for the webview
        const editorSourceDirPath = path.join(this._context.extensionUri.fsPath, 'src', 'editor', 'definitions');

        const scriptUri = webview.asWebviewUri(vscode.Uri.parse(path.join(editorSourceDirPath, 'definitionVisualEditor.js')));
        const styleMainUri = webview.asWebviewUri(vscode.Uri.parse(path.join(editorSourceDirPath, 'definitionEditor.css')));

        const jsonNodeModulesPath = path.join(this._context.extensionUri.fsPath, 'node_modules');

        const jsonEditorPath = vscode.Uri.parse(path.join(jsonNodeModulesPath, '@json-editor', 'json-editor', 'dist', 'jsoneditor.js'));

        const jsonEditorScriptUri = webview.asWebviewUri(jsonEditorPath);


        // Use a nonce to whitelist which scripts can be run
        const nonce = getNonce();

        return `
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
                <button id='submit'>Save</button>
                <button id='delete'>Delete</button>
                <button id='validate'>Validate</button>
                <div id="source-div">
                    <label id="source-label">Definition's File</label>
                    <input id="source" value="test value" disabled/>
                </div>
                <div id="main"></div>
                <script src="${scriptUri}" http-equiv="Content-Security-Policy" script-src-elem 'unsafe-inline' ${scriptUri} nonce='${nonce}';></script>
            </body>
            </html>`;
    }

    private postEditMessage(panel: vscode.WebviewPanel, body: AacDefinitionEdit): void {
        this.postMessage(panel, AacEditorEventTypes.EDIT, body);
    }

    /**
     * Send a message to the editor.
     */
    private postMessage(panel: vscode.WebviewPanel, type: AacEditorEventTypes, body: any): void {
        panel.webview.postMessage({ type, body });
    }

    /**
     * On messages from the editor, perform the appropriate action.
     */
    private onMessage(panel: vscode.WebviewPanel, document: AacDefinitionsDocument, message: any) {
        const params = new URLSearchParams(document.uri.query);
        const isNewDefinition = params.get(queryKeys.QUERY_KEY_NEW) == `${true}`
        let definitionName = params.get(queryKeys.QUERY_KEY_NAME)
        let definitionSourceFile = params.get(queryKeys.QUERY_KEY_FILE)
        let definitionSchema = params.get(queryKeys.QUERY_KEY_SCHEMA)

        switch (message.type) {
            case AacEditorEventTypes.READY:
                if (isNewDefinition) {}
                this.getInitFormData(document, isNewDefinition, definitionName ?? "", definitionSourceFile ?? "", definitionSchema ?? "").then(formData => {
                    this.postEditMessage(panel, formData);
                })
                return;
            case AacEditorEventTypes.EDIT:
                document.makeEdit(message.body as AacDefinitionEdit);
                return;
            case AacEditorEventTypes.SAVE:
                if (isNewDefinition && document.documentState == AacDocumentStateTypes.NEW ) {
                    this.createDefinition(document);
                } else {
                    this.updateDefinition(document);
                }
                return;
            case AacEditorEventTypes.DELETE:
                vscode.commands.executeCommand('workbench.action.closeActiveEditor');
                this.deleteDefinition(document);
                return;
            case AacEditorEventTypes.VALIDATE:
                this.validateDefinition(document);
                return;
        }
    }

    private async getInitFormData(document: AacDefinitionsDocument, isNew: boolean, definitionName: string, definitionSource: string, definitionSchema: string): Promise<AacDefinitionEdit> {
        // Either get the info necessary to create a scaffold for a new definition, or get the definition to edit.
        let definitionInfo: AacDefinitionEdit
        if (isNew) {
            document.documentState = AacDocumentStateTypes.NEW
            let jsonSchemaResponse = await aacRestApi.getRootKeySchemaContextSchemaGet(definitionSchema)
            definitionInfo =  {
                name: definitionName,
                sourceUri: URI.parse(definitionSource).fsPath,
                jsonSchema: jsonSchemaResponse.body?.jsonSchema,
                rootKey: definitionSchema
            } as AacDefinitionEdit
        } else {
            document.documentState = AacDocumentStateTypes.UPDATE
            definitionInfo =  await aacRestApi.getDefinitionByNameDefinitionGet(definitionName, true).then(response => {
                return response.body as AacDefinitionEdit
            });
        }

        return definitionInfo;
    }

    private async getDefinition(document: AacDefinitionsDocument):  Promise<{ response: IncomingMessage; body: DefinitionModel; }>  {
        return Promise.resolve(aacRestApi.getDefinitionByNameDefinitionGet(document.originalDefinitionName, true));
    }

    private async createDefinition(document: AacDefinitionsDocument): Promise<IncomingMessage> {
        const updatedDefinitionModel: DefinitionModel = new DefinitionModel();
        updatedDefinitionModel.name = document.originalDefinitionName;
        updatedDefinitionModel.sourceUri = URI.parse(document.originalDefinitionUri).fsPath;
        updatedDefinitionModel.structure = document.definitionStructure ?? {};

        const response = (await Promise.resolve(aacRestApi.addDefinitionDefinitionPost(updatedDefinitionModel))).response;
        if (response.statusCode !== 204) {
            vscode.window.showErrorMessage(`Failed to update definition: ${response.statusMessage}`);
        };

        document.documentState = AacDocumentStateTypes.UPDATE
        return response;
    }

    private async updateDefinition(document: AacDefinitionsDocument): Promise<IncomingMessage> {
        const updatedDefinitionModel: DefinitionModel = new DefinitionModel();
        updatedDefinitionModel.name = document.originalDefinitionName;
        updatedDefinitionModel.sourceUri = URI.parse(document.originalDefinitionUri).fsPath;
        updatedDefinitionModel.structure = document.definitionStructure ?? {};

        const response = (await Promise.resolve(aacRestApi.updateDefinitionDefinitionPut(updatedDefinitionModel))).response;
        if (response.statusCode !== 204) {
            vscode.window.showErrorMessage(`Failed to update definition: ${response.statusMessage}`);
        };

        document.documentState = AacDocumentStateTypes.UPDATE
        return response;
    }

    private async deleteDefinition(document: AacDefinitionsDocument): Promise<IncomingMessage> {
        const response = (await Promise.resolve(aacRestApi.removeDefinitionByNameDefinitionDelete(document.originalDefinitionName))).response;
        if (response.statusCode !== 204) {
            vscode.window.showErrorMessage(`Failed to delete definition: ${response.statusMessage}`);
        };

        return response;
    }

    private async validateDefinition(document: AacDefinitionsDocument): Promise<IncomingMessage> {
        const validateCommandName = "validate";
        const validateDefinitionNameArg = "--definition-name";
        const commandRequest = new CommandRequestModel();
        commandRequest.name = validateCommandName;
        commandRequest.arguments = [document.originalDefinitionUri, validateDefinitionNameArg, document.originalDefinitionName];

        const {response, body} = (await Promise.resolve(aacRestApi.executeAacCommandCommandPost(commandRequest)));

        if (body.success) {
            vscode.window.showInformationMessage(body.resultMessage);
        } else {
            vscode.window.showErrorMessage(body.resultMessage);
        };

        return response;
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

        webviewPanel.onDidDispose(() => this._webviews.delete(entry));
    }
}

