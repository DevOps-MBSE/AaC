import * as vscode from 'vscode';
import { URI } from 'vscode-uri';
import { aacRestApi, DefinitionModel } from "../requests/aacRequests";
import * as queryKeys from './queryKeyConstants'

export class AacDefinitionsViewProvider implements vscode.TreeDataProvider<Definition> {

    public COMMAND_DEFINITIONS_LIST_REFRESH = "definitionsList.refreshEntry";
    public COMMAND_DEFINITIONS_LIST_CREATE = "definitionsList.createEntry";
    public COMMAND_DEFINITIONS_LIST_EDIT = "definitionsList.editEntry";
    public COMMAND_DEFINITIONS_LIST_DELETE = "definitionsList.deleteEntry";
    private _onDidChangeTreeData: vscode.EventEmitter<Definition | undefined | void> = new vscode.EventEmitter<Definition | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<Definition | undefined | void> = this._onDidChangeTreeData.event;

    constructor() { }

    public getTreeItem(element: Definition): vscode.TreeItem {
        return element;
    }

    public getChildren(element?: Definition): Thenable<Definition[]> {
        if (element) {
            return Promise.resolve(
                this.getDefinitionsInContext()
            );
        } else {
            return Promise.resolve(this.getDefinitionsInContext());
        }
    }

    public refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    private async getDefinitionsInContext(): Promise<Definition[]> {
        const requestResponse = (await Promise.resolve(aacRestApi.getDefinitionsDefinitionsGet()));
        return requestResponse.body.map((definition: DefinitionModel) => new Definition(definition, vscode.TreeItemCollapsibleState.None));
    }
}

export class Definition extends vscode.TreeItem {
    constructor(
        public readonly definitionModel: DefinitionModel,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {

        super(definitionModel.name, collapsibleState);
        this.definitionType = Object.keys(definitionModel.structure)[0];
        this.description = `${this.definitionType}`;
        this.tooltip = `Open the ${this.definitionType} definition "${definitionModel.name}" in a visual editor.\nThe definition originates from ${definitionModel.sourceUri}`;
        this.iconPath = {
            light: "",
            dark:  ""
        };
    }

    private definitionType: string;
}

export async function createDefinition() {
    // Prompt the user to pick an AaC file to store the new definition in.
    const definitionFileOpenDialogOptions: vscode.OpenDialogOptions = {
        title: "Select the AaC file for the new definition.",
        canSelectMany: false,
        canSelectFolders: false,
    };

    let fileUris: vscode.Uri[] | undefined = await vscode.window.showOpenDialog(definitionFileOpenDialogOptions);

    // Prompt the user to name the new definition.
    const newDefinitionNameInputBoxOptions: vscode.InputBoxOptions = {
        title: "Enter a name for the new definition.",
    };

    let newDefinitionName: string | undefined = await vscode.window.showInputBox(newDefinitionNameInputBoxOptions);

    // Prompt the user to choose the definition's schema type (root key).
    const newDefinitionRootKeyQuickPick: vscode.QuickPickOptions = {
        title: `Pick the schema type for ${newDefinitionName}.`,
        canPickMany: false,
    };

    let quickPickRootKeys: string[] = await aacRestApi.getLanguageContextRootKeysContextRootKeysGet().then(response => {
        return response.body ? response.body as string[] : []
    })


    let newDefinitionSchema: string | undefined = await vscode.window.showQuickPick(quickPickRootKeys, newDefinitionRootKeyQuickPick);

    if (newDefinitionSchema && newDefinitionName && fileUris?.length && fileUris?.length > 0) {
        const query = createDocumentQuery(true, fileUris[0], newDefinitionName, newDefinitionSchema)
        openDefinitionFile(newDefinitionName, query)
    }
}

function getDefinitionByName(definitionName: string) {
    return Promise.resolve(aacRestApi.getDefinitionByNameDefinitionGet(definitionName, true));
}

export function editDefinition(event: Definition) {
    if (Object.keys(event.definitionModel).length > 0) {
        getDefinitionByName(event.definitionModel.name).then(response => {
            const query = createDocumentQuery(false, URI.file(response.body.sourceUri), response.body.name)
            openDefinitionFile(response.body.name, query)
        });
    }
}

function deleteDefinitionByName(definitionName: string) {
    return Promise.resolve(aacRestApi.removeDefinitionByNameDefinitionDelete(definitionName));
}

export function deleteDefinition(event: Definition, viewProvider: AacDefinitionsViewProvider) {
    if (Object.keys(event.definitionModel).length > 0) {
        deleteDefinitionByName(event.definitionModel.name).then(() => {
            viewProvider.refresh();
        });
    }
}

// Executed when a user selects a definition 'node' in the VSCode treeview listing the definitions in the context.
export function onDefinitionNodeSelection(event: vscode.TreeViewSelectionChangeEvent<Definition>) {
    if (event.selection.length > 0) {
        editDefinition(event.selection[0]);
    }
}

function createDocumentQuery(isNewDefinition: boolean, file: vscode.Uri, name: string, schema: string = ""): string {
    return `${queryKeys.QUERY_KEY_NEW}=${isNewDefinition}&` +
        `${queryKeys.QUERY_KEY_FILE}=${file}&` +
        `${queryKeys.QUERY_KEY_NAME}=${name}&` +
        `${queryKeys.QUERY_KEY_SCHEMA}=${schema}`
}

function openDefinitionFile(definitionName: string, documentQuery: string) {
    vscode.commands.executeCommand(
        "vscode.openWith",
        vscode.Uri.from({scheme: "untitled", path: definitionName, query: documentQuery}),
        "aac.visualEditor"
    );
}
