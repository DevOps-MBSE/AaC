import * as vscode from 'vscode';
import { Disposable } from '../../disposable';

export interface AacDefinitionsDocumentDelegate {
    getFileData(): Promise<Uint8Array>;
}

/**
 * Define the edit datastructure.
 */
export interface AacDefinitionEdit {
    readonly name: string;
    readonly source_uri: string;
    readonly structure: Object;
}

/**
 * Define the document data model used for AaC Definitions.
 */
export class AacDefinitionsDocument extends Disposable implements vscode.CustomDocument {

    static async create(
        uri: vscode.Uri,
        backupId: string | undefined,
        delegate: AacDefinitionsDocumentDelegate,
    ): Promise<AacDefinitionsDocument | PromiseLike<AacDefinitionsDocument>> {
        //# TODO Set the initial file data here.

        // If we have a backup, read that. Otherwise read the resource from the workspace
        const dataFile = typeof backupId === 'string' ? vscode.Uri.parse(backupId) : uri;
        const fileData = await AacDefinitionsDocument.readFile(dataFile);
        return new AacDefinitionsDocument(uri, fileData, delegate);
    }

    private static async readFile(uri: vscode.Uri): Promise<Uint8Array> {
        if (uri.scheme === 'untitled') {
            return new Uint8Array();
        }
        return new Uint8Array(await vscode.workspace.fs.readFile(uri));
    }

    private readonly _uri: vscode.Uri;

    private _documentData: Uint8Array;
    private _edits: Array<AacDefinitionEdit> = [];
    private _savedEdits: Array<AacDefinitionEdit> = [];

    private readonly _delegate: AacDefinitionsDocumentDelegate;

    private constructor(
        uri: vscode.Uri,
        initialContent: Uint8Array,
        delegate: AacDefinitionsDocumentDelegate
    ) {
        super();
        this._uri = uri;
        this._documentData = initialContent;
        this._delegate = delegate;
    }

    public get uri() { return this._uri; }

    public get documentData(): Uint8Array { return this._documentData; }

    private readonly _onDidDispose = this._register(new vscode.EventEmitter<void>());

    /**
     * Fired when the document is disposed of.
     */
    public readonly onDidDispose = this._onDidDispose.event;

    private readonly _onDidChangeDocument = this._register(new vscode.EventEmitter<{
        readonly content?: Uint8Array;
        readonly edits: readonly AacDefinitionEdit[];
    }>());

    /**
     * Fired to notify webviews that the document has changed.
     */
    public readonly onDidChangeContent = this._onDidChangeDocument.event;

    private readonly _onDidChange = this._register(new vscode.EventEmitter<{
        readonly label: string,
        undo(): void,
        redo(): void,
    }>());

    /**
     * Fired to tell VS Code that an edit has occurred in the document.
     *
     * This updates the document's dirty indicator.
     */
    public readonly onDidChange = this._onDidChange.event;

    /**
     * Called by VS Code when there are no more references to the document.
     *
     * This happens when all editors for it have been closed.
     */
    dispose(): void {
        this._onDidDispose.fire();
        super.dispose();
    }

    /**
     * Called when the user edits the document in a webview.
     *
     * This fires an event to notify VS Code that the document has been edited.
     */
    makeEdit(edit: AacDefinitionEdit) {
        this._edits.push(edit);

        this._onDidChange.fire({
            label: 'Stroke',
            undo: async () => {
                this._edits.pop();
                this._onDidChangeDocument.fire({
                    edits: this._edits,
                });
            },
            redo: async () => {
                this._edits.push(edit);
                this._onDidChangeDocument.fire({
                    edits: this._edits,
                });
            }
        });
    }

    /**
     * Called by VS Code when the user saves the document.
     */
    async save(cancellation: vscode.CancellationToken): Promise<void> {
        // await this.saveAs(this.uri, cancellation);
        console.log("save")
        this._savedEdits = Array.from(this._edits);
    }

    /**
     * Called by VS Code when the user saves the document to a new location.
     */
    async saveAs(targetResource: vscode.Uri, cancellation: vscode.CancellationToken): Promise<void> {
        const fileData = await this._delegate.getFileData();
        if (cancellation.isCancellationRequested) {
            return;
        }
        await vscode.workspace.fs.writeFile(targetResource, fileData);
    }

    /**
     * Called by VS Code when the user calls `revert` on a document.
     */
    async revert(_cancellation: vscode.CancellationToken): Promise<void> {
        const diskContent = await AacDefinitionsDocument.readFile(this.uri);
        this._documentData = diskContent;
        this._edits = this._savedEdits;
        this._onDidChangeDocument.fire({
            content: diskContent,
            edits: this._edits,
        });
    }

    /**
     * Called by VS Code to backup the edited document.
     *
     * These backups are used to implement hot exit.
     */
    async backup(destination: vscode.Uri, cancellation: vscode.CancellationToken): Promise<vscode.CustomDocumentBackup> {
        await this.saveAs(destination, cancellation);

        return {
            id: destination.toString(),
            delete: async () => {
                try {
                    await vscode.workspace.fs.delete(destination);
                } catch {
                    // noop
                }
            }
        };
    }
}