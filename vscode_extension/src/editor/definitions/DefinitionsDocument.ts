import * as vscode from 'vscode';
import * as path from 'path';
import { Disposable } from '../../disposable';
import { aacRestApi, DefinitionModel } from "../../requests/aacRequests";
import { IncomingMessage } from 'http';

export enum AacEditorEventTypes {
    READY = 1,
    EDIT = 2,
    SAVE = 3
}

/**
 * Define the edit datastructure.
 */
export interface AacDefinitionEdit {
    readonly name: string;
    readonly sourceUri: string;
    readonly structure: Object;
    readonly jsonSchema?: Object;
}

/**
 * Define the edit datastructure.
 */
export interface AacDefinitionDelegate {
    getDefinition(document: AacDefinitionsDocument):  Promise<{ response: IncomingMessage; body: DefinitionModel; }>;
    updateDefinition(document: AacDefinitionsDocument): Promise<IncomingMessage>;
}

/**
 * Define the document data model used for AaC Definitions.
 */
export class AacDefinitionsDocument extends Disposable implements vscode.CustomDocument {

    static async create(
        uri: vscode.Uri,
        delegate: AacDefinitionDelegate
    ): Promise<AacDefinitionsDocument | PromiseLike<AacDefinitionsDocument>> {
        return new AacDefinitionsDocument(uri, delegate);
    }

    private readonly _documentUri: vscode.Uri;
    private readonly _delegate: AacDefinitionDelegate;

    //VSCode document attributes
    private _edits: Array<AacDefinitionEdit> = [];
    private _savedEdits: Array<AacDefinitionEdit> = [];

    // AaC Definition Data Attributes
    private _originalDefinitionName: string;
    private _originalDefinitionUri: string;
    private _definitionStructure?: Object;
    private _jsonSchema?: Object;


    private constructor(
        uri: vscode.Uri,
        delegate: AacDefinitionDelegate
    ) {
        super();
        this._documentUri = uri;
        this._delegate = delegate;
        this._originalDefinitionName = path.basename(uri.path);
        this._originalDefinitionUri = "";

        this._delegate.getDefinition(this).then(response => {
            this._definitionStructure = response.body.structure;
            this._originalDefinitionUri = response.body.sourceUri;
            this._jsonSchema = response.body.jsonSchema;
        });
    }

    public get uri() { return this._documentUri; }
    public get originalDefinitionName() { return this._originalDefinitionName; }
    public get originalDefinitionUri() { return this._originalDefinitionUri; }
    public get definitionStructure() { return this._definitionStructure; }

    private readonly _onDidDispose = this._register(new vscode.EventEmitter<void>());

    /**
     * Fired when the document is disposed of.
     */
    public readonly onDidDispose = this._onDidDispose.event;

    private readonly _onDidChangeDocument = this._register(new vscode.EventEmitter<{
        readonly content?: Object;
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
        this._definitionStructure = edit.structure;

        this._onDidChange.fire({
            label: 'edit',
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
    async save(_cancellation: vscode.CancellationToken): Promise<void> {
        this._delegate.updateDefinition(this);
    }

    /**
     * Called by VS Code when the user saves the document to a new location.
     */
    async saveAs(_targetResource: vscode.Uri, cancellation: vscode.CancellationToken): Promise<void> {

        if (cancellation.isCancellationRequested) {
            return;
        }

        this._delegate.updateDefinition(this);
    }

    /**
     * Called by VS Code when the user calls `revert` on a document.
     */
    async revert(_cancellation: vscode.CancellationToken): Promise<void> {
        // TODO - Read the document representation/backup from file/disk
        this._definitionStructure = await this._delegate.getDefinition(this);
        this._edits = this._savedEdits;
        this._onDidChangeDocument.fire({
            content: this._definitionStructure,
            edits: this._edits,
        });
    }

    /**
     * Called by VS Code to backup the edited document.
     *
     * These backups are used to implement hot exit.
     */
    async backup(destination: vscode.Uri, _cancellation: vscode.CancellationToken): Promise<vscode.CustomDocumentBackup> {
        // TODO - Write the document representation to file/disk

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

   /**
     * Get the definition structure/object
     * @returns an Object that is the definition's structure
     */
    async getDefinitionStructure(): Promise<Object> {
        return this._definitionStructure ? this._definitionStructure : {};
    }

    /**
     * Get the JSON Schema for the definition
     * @returns an Object that is the definition's JSON schema
     */
    async getDefinitionSchema(): Promise<Object> {
        return this._jsonSchema ? this._jsonSchema : {};
    }
}